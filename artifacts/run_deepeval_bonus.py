from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Any

os.environ["DEEPEVAL_TELEMETRY_OPT_OUT"] = "YES"

from deepeval.metrics import ContextualPrecisionMetric
from deepeval.models import DeepEvalBaseLLM
from deepeval.test_case import LLMTestCase


TOKEN_PATTERN = re.compile(r"\b\w+\b", flags=re.UNICODE)
RELEVANCE_THRESHOLD = 0.65


def tokens(text: str) -> set[str]:
    return set(TOKEN_PATTERN.findall(text.casefold()))


def relevance_verdicts(
    retrieved_contexts: list[str], gold_contexts: list[str]
) -> list[bool]:
    gold_token_sets = [tokens(context) for context in gold_contexts]
    verdicts = []
    for retrieved in retrieved_contexts:
        retrieved_tokens = tokens(retrieved)
        best_containment = max(
            (
                len(retrieved_tokens & gold_tokens) / len(gold_tokens)
                for gold_tokens in gold_token_sets
                if gold_tokens
            ),
            default=0.0,
        )
        verdicts.append(best_containment >= RELEVANCE_THRESHOLD)
    return verdicts


class OfflineVerdictModel(DeepEvalBaseLLM):
    """Feeds deterministic local relevance labels into DeepEval's AP metric."""

    def __init__(self, verdicts: list[bool]) -> None:
        self._verdicts = verdicts
        super().__init__(model="offline-gold-context-overlap")

    def load_model(self, *args: Any, **kwargs: Any) -> "OfflineVerdictModel":
        return self

    def generate(self, prompt: Any, schema: Any = None, **kwargs: Any) -> Any:
        payload = {
            "verdicts": [
                {
                    "verdict": "yes" if verdict else "no",
                    "reason": "deterministic offline gold-context containment",
                }
                for verdict in self._verdicts
            ]
        }
        return schema(**payload) if schema is not None else json.dumps(payload)

    async def a_generate(
        self, prompt: Any, schema: Any = None, **kwargs: Any
    ) -> Any:
        return self.generate(prompt, schema=schema, **kwargs)

    def get_model_name(self, *args: Any, **kwargs: Any) -> str:
        return "offline-gold-context-overlap"


root = Path(__file__).resolve().parent.parent
gold = json.loads((root / "golden_dataset.json").read_text(encoding="utf-8"))
actual = json.loads(
    (root / "artifacts" / "actual_answers.json").read_text(encoding="utf-8")
)
gold_by_id = {record["id"]: record for record in gold["qa_pairs"]}
results = []
for record in actual["answers"]:
    golden = gold_by_id[record["id"]]
    retrieved = [item["text"] for item in record["retrieved_contexts"]]
    gold_contexts = [item["text"] for item in golden["contexts"]]
    model = OfflineVerdictModel(relevance_verdicts(retrieved, gold_contexts))
    metric = ContextualPrecisionMetric(
        threshold=0.9,
        model=model,
        include_reason=False,
        async_mode=False,
    )
    test_case = LLMTestCase(
        input=golden["question"],
        actual_output=record["actual_answer"],
        expected_output=golden["expected_answer"],
        retrieval_context=retrieved,
    )
    score = float(metric.measure(test_case, _show_indicator=False))
    results.append({"id": record["id"], "score": score})
    print(f"DeepEval {record['id']}: {score:.6f}", flush=True)

output = {
    "framework": "deepeval",
    "version": "4.1.7",
    "metric": "ContextualPrecisionMetric",
    "judge": "offline gold-context token containment",
    "relevance_threshold": RELEVANCE_THRESHOLD,
    "quality_gate": 0.9,
    "results": results,
}
(root / "artifacts" / "bonus_deepeval_results.json").write_text(
    json.dumps(output, indent=2) + "\n", encoding="utf-8"
)
