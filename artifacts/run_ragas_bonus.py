from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

os.environ["RAGAS_DO_NOT_TRACK"] = "true"

from ragas.dataset_schema import SingleTurnSample
from ragas.metrics import NonLLMContextPrecisionWithReference
from ragas.metrics.base import MetricType, SingleTurnMetric


TOKEN_PATTERN = re.compile(r"\b\w+\b", flags=re.UNICODE)
RELEVANCE_THRESHOLD = 0.65


def tokens(text: str) -> set[str]:
    return set(TOKEN_PATTERN.findall(text.casefold()))


@dataclass
class GoldContextContainment(SingleTurnMetric):
    """Fraction of a gold context's tokens present in a retrieved chunk."""

    name: str = "gold_context_containment"
    _required_columns: dict[MetricType, set[str]] = field(
        default_factory=lambda: {
            MetricType.SINGLE_TURN: {"reference", "response"}
        }
    )

    def init(self, run_config: Any) -> None:
        return None

    async def _single_turn_ascore(
        self, sample: SingleTurnSample, callbacks: Any
    ) -> float:
        retrieved_tokens = tokens(sample.reference or "")
        gold_tokens = tokens(sample.response or "")
        if not gold_tokens:
            return 0.0
        return len(retrieved_tokens & gold_tokens) / len(gold_tokens)

    async def _ascore(self, row: dict[str, Any], callbacks: Any) -> float:
        return await self._single_turn_ascore(
            SingleTurnSample(**row), callbacks
        )


root = Path(__file__).resolve().parent.parent
gold = json.loads((root / "golden_dataset.json").read_text(encoding="utf-8"))
actual = json.loads(
    (root / "artifacts" / "actual_answers.json").read_text(encoding="utf-8")
)
gold_by_id = {record["id"]: record for record in gold["qa_pairs"]}
metric = NonLLMContextPrecisionWithReference(
    distance_measure=GoldContextContainment(),
    threshold=RELEVANCE_THRESHOLD,
)

results = []
for record in actual["answers"]:
    golden = gold_by_id[record["id"]]
    sample = SingleTurnSample(
        retrieved_contexts=[item["text"] for item in record["retrieved_contexts"]],
        reference_contexts=[item["text"] for item in golden["contexts"]],
    )
    score = float(metric.single_turn_score(sample))
    results.append({"id": record["id"], "score": score})
    print(f"RAGAS {record['id']}: {score:.6f}", flush=True)

output = {
    "framework": "ragas",
    "version": "0.4.3",
    "metric": "NonLLMContextPrecisionWithReference",
    "judge": "offline gold-context token containment",
    "relevance_threshold": RELEVANCE_THRESHOLD,
    "quality_gate": 0.9,
    "results": results,
}
(root / "artifacts" / "bonus_ragas_results.json").write_text(
    json.dumps(output, indent=2) + "\n", encoding="utf-8"
)
