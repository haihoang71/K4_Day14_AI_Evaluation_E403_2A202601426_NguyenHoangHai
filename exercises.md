# Day 14 — Exercises

## AI Evaluation & Benchmarking · Lab Worksheet

**Thời gian làm bài:** 14:15–17:00

**Domain:** OrbitTech Store Customer Support

Điền trực tiếp câu trả lời vào file này. Golden dataset 20 QA được viết một lần
duy nhất trong `golden_dataset.json`, không chép lại toàn bộ vào Markdown.

---

Từ 14:15–14:30, cài môi trường và chạy baseline tests theo `guide_lab.md`.

---

## Part 1 — Warm-up (14:30–14:45)

### Exercise 1.1 — RAGAS Metric Thresholds

Theo bài giảng:

- 0.8–1.0: Good — monitor, maintain.
- 0.6–0.8: Needs work — analyze failures, iterate.
- Dưới 0.6: Significant issues — investigate.

Với từng metric, xác định khi nào score thấp có thể chấp nhận và khi nào là
critical.

| Metric | Acceptable Low Score Scenario | Critical Low Score Scenario | Action Required |
|---|---|---|---|
| Faithfulness | Câu trả lời có phần diễn giải hoặc chào hỏi không xuất hiện nguyên văn trong context nhưng các khẳng định chính vẫn có nguồn; score 0.6–0.8 có thể chấp nhận tạm thời. | Score < 0.6 ở câu hỏi chính sách, thanh toán, bảo hành; đặc biệt khi answer đưa ra điều kiện hoặc cam kết không có trong nguồn. | Kiểm tra grounding theo từng claim, bổ sung citation, siết prompt chỉ trả lời từ context và chặn deploy nếu lỗi liên quan chính sách. |
| Answer Relevance | Câu hỏi mở hoặc cần giải thích nhiều bước khiến answer chứa thêm thông tin hữu ích; score 0.6–0.8 nhưng vẫn giải quyết đúng intent. | Score < 0.6 do trả lời sai intent, lạc sang sản phẩm/chính sách khác hoặc không trả lời câu hỏi trực tiếp. | Cải thiện intent routing và prompt, thêm test theo category, rút gọn phần ngoài yêu cầu. |
| Context Recall | Một câu hỏi đơn giản vẫn được trả lời đúng từ một chunk dù gold answer có vài chi tiết phụ; score hơi thấp có thể theo dõi. | Score < 0.6 khi thiếu điều kiện, ngoại lệ, mốc thời gian hoặc evidence bắt buộc để tạo câu trả lời đúng. | Điều chỉnh chunking/query expansion/top-k, bổ sung metadata filter và kiểm tra coverage của source documents. |
| Context Precision | Relevant evidence vẫn có trong top-k nhưng đứng sau một vài chunk nhiễu; answer cuối vẫn đúng nên có thể chấp nhận tạm thời. | Score < 0.6 làm context window bị lấp bởi nhiễu, relevant chunks xếp quá muộn hoặc generator dùng nhầm chính sách. | Thêm reranker, cải thiện embedding/query, lọc metadata và đo Precision theo từng vị trí. |
| Completeness | Answer đúng phần cốt lõi nhưng thiếu chi tiết tùy chọn hoặc hướng dẫn bổ sung ít ảnh hưởng; score 0.6–0.8. | Score < 0.6 vì bỏ sót bước bắt buộc, điều kiện eligibility, ngoại lệ, phí hoặc deadline. | Dùng checklist theo loại câu hỏi, cải thiện retrieval recall và yêu cầu generator đối chiếu đủ các ý trong evidence. |

### Exercise 1.2 — Bias trong LLM-as-a-Judge

Ba bias thường gặp:

- Position bias: judge ưu tiên answer xuất hiện trước.
- Verbosity bias: judge ưu tiên answer dài hơn.
- Self-preference: judge ưu tiên output giống chính model đó.

**Câu 1: Thiết kế experiment phát hiện position bias với ít nhất hai conditions.**

> *Câu trả lời:* Chuẩn bị các cặp answer A/B đã được human chấm và có chất lượng
> tương đương hoặc biết trước answer tốt hơn. Condition 1 cho judge xem A trước,
> B sau; Condition 2 đảo thứ tự B trước, A sau, đồng thời giữ nguyên prompt,
> rubric, model và tham số sinh. Chạy nhiều cặp, randomize thứ tự và so sánh tỷ lệ
> thắng/điểm của cùng một answer giữa hai condition. Nếu answer đứng đầu nhận điểm
> cao hơn một cách có ý nghĩa thống kê bất kể nội dung, judge có position bias.

**Câu 2: Làm thế nào giảm verbosity bias bằng rubric design?**

> *Câu trả lời:* Rubric phải tách correctness, completeness, relevance và clarity;
> mô tả rõ rằng độ dài không phải tiêu chí, thông tin lặp hoặc ngoài yêu cầu không
> được cộng điểm và có thể bị trừ ở relevance/conciseness. Mỗi mức 1–5 cần có
> anchor theo số ý đúng, số lỗi và mức độ bao phủ evidence. Có thể yêu cầu judge
> trích các claim đáp ứng tiêu chí trước khi cho điểm để buộc điểm dựa trên nội dung.

**Câu 3: Tại sao cần calibrate LLM judge với human labels?**

> *Câu trả lời:* Human labels là mốc tham chiếu để đo judge có thực sự phản ánh
> tiêu chuẩn nghiệp vụ hay chỉ nhất quán với thiên kiến của model. Calibration giúp
> chọn rubric/threshold, phát hiện leniency, severity, position và self-preference
> bias, đồng thời đo agreement với chuyên gia. Với các case bất đồng hoặc rủi ro cao,
> human review vẫn là quyết định cuối cùng.

### Exercise 1.3 — Evaluation trong CI/CD

**Câu 1: Chọn threshold để block deployment.**

| Metric | Threshold | Lý do |
|---|---:|---|
| Faithfulness | 0.80 | Hallucination có thể tạo cam kết sai về giá, đổi trả hoặc bảo hành; đây là quality gate nghiêm ngặt nhất. |
| Answer Relevance | 0.70 | Answer phải giải quyết đúng intent nhưng vẫn cho phép một lượng nhỏ hướng dẫn bổ sung hữu ích. |
| Completeness | 0.75 | Cần bao phủ phần lớn điều kiện và các bước bắt buộc; thiếu chi tiết nhỏ chưa nhất thiết phải chặn release. |

**Câu 2: Khi nào dùng offline evaluation, online evaluation và human review?**

> *Câu trả lời:* Dùng **offline evaluation** trên golden dataset cho mọi thay đổi
> code, prompt, model, retriever và trước release để phát hiện regression có thể tái
> lập. Dùng **online evaluation** sau triển khai để theo dõi traffic thật, drift,
> latency, cost, feedback và các intent chưa có trong dataset. Dùng **human review**
> để hiệu chỉnh LLM judge, xử lý case bất đồng/khó, audit mẫu định kỳ và duyệt các
> câu trả lời rủi ro cao liên quan thanh toán, quyền riêng tư, bảo hành hoặc escalation.

---

## Part 2 — Core Coding (14:45–15:40)

Hoàn thiện các TODO bắt buộc trong `template.py`.

**Kết quả thực hiện đến Checkpoint 2**

| Checkpoint | Trạng thái | Kết quả |
|---|---|---|
| Task 1 — Data Models | Hoàn thành | `QAPair`, `EvalResult` và `overall_score()` đã được triển khai; 3/3 targeted tests pass. |
| Task 2 — RAGASEvaluator | Hoàn thành | Ba answer-side metrics, hai retrieval-side metrics và `run_full_eval()` đã được triển khai; 14 targeted tests pass, 1 bonus test skipped. |
| Task 3–5 | Chưa thực hiện | Giữ nguyên cho các checkpoint tiếp theo. |

### Task 1 — Data Models

- `QAPair`: question, expected answer, gold context, metadata và retrieved contexts.
- `EvalResult`: answer-side scores, optional retrieval scores, pass/failure fields.
- `overall_score()`: trung bình Faithfulness, Relevance và Completeness.

### Task 2 — RAGASEvaluator

Answer-side:

- `evaluate_faithfulness(answer, context)`
- `evaluate_relevance(answer, question)`
- `evaluate_completeness(answer, expected)`

Retrieval-side:

- `evaluate_context_recall(contexts, expected)`
- `evaluate_context_precision(contexts, expected)`

Full pipeline:

- `run_full_eval(..., contexts=None)` luôn tính ba answer metrics.
- Nếu có `contexts`, tính và lưu thêm Context Recall và Context Precision.
- Retrieval scores không làm thay đổi `overall_score()` và pass rule gốc.

### Task 3 — LLMJudge

- `score_response(question, answer, rubric)`
- `detect_bias(scores_batch)`

### Task 4 — BenchmarkRunner

- `run(qa_pairs, agent_fn, evaluator)`
- `generate_report(results)`
- `run_regression(new_results, baseline_results)`
- `identify_failures(results, threshold)`

`BenchmarkRunner.run()` phải truyền `pair.retrieved_contexts` vào
`run_full_eval()`. Report phải có average của hai retrieval metrics.

### Task 5 — FailureAnalyzer

- `categorize_failures(failures)`
- `find_root_cause(failure)`
- `generate_improvement_suggestions(failures)`
- `generate_improvement_log(failures, suggestions)`

Kiểm tra:

```bash
pytest tests/ -v
```

`rerank_by_overlap()` là TODO bonus của Exercise 3.5. Test tương ứng được skip
nếu bạn chưa làm bonus.

---

## Part 3 — Golden Dataset & Real Benchmark (15:40–16:35)

### Exercise 3.1 — Build the Golden Dataset

Thiết kế và validate dataset theo Mục 5–6 trong `guide_lab.md`. Nội dung 20 QA
được điền trực tiếp trong `golden_dataset.json`; phần dưới chỉ ghi lại kết quả
và quyết định thiết kế, không chép lại toàn bộ QA.

**Kết quả dataset**

| Hạng mục | Kết quả |
|---|---|
| Tổng số records | ____ / 20 |
| Easy | ____ / 5 |
| Medium | ____ / 7 |
| Hard | ____ / 5 |
| Adversarial | ____ / 3 |
| Source documents được sử dụng | ____ / 10 |
| Validator status | PASS / FAIL |

**Ba case đại diện cho quyết định thiết kế**

| ID | Difficulty | Source document(s) | Vì sao case phù hợp với difficulty/attack type? |
|---|---|---|---|
| | | | |
| | | | |
| | | | |

**Điểm khó nhất khi xây dựng expected answer hoặc evidence là gì?**

> *Câu trả lời:*

**Xác nhận:**

- [ ] Mọi claim trong expected answer đều có evidence hỗ trợ.
- [ ] Không có questions trùng ý và không dùng kiến thức ngoài corpus.
- [ ] `python validate_golden_dataset.py` báo `PASS`.

### Exercise 3.2 — Benchmark Run

Chạy:

```bash
python domain_assistant.py
python evaluate_answers.py
```

Copy bảng terminal vào đây hoặc điền từ `artifacts/benchmark_results.json`.

| ID | Question (short) | Ctx Recall | Ctx Precision | Faithfulness | Relevance | Completeness | Overall | Passed? | Failure Type |
|---|---|---:|---:|---:|---:|---:|---:|---|---|
| E01 | | | | | | | | | |
| E02 | | | | | | | | | |
| E03 | | | | | | | | | |
| E04 | | | | | | | | | |
| E05 | | | | | | | | | |
| M01 | | | | | | | | | |
| M02 | | | | | | | | | |
| M03 | | | | | | | | | |
| M04 | | | | | | | | | |
| M05 | | | | | | | | | |
| M06 | | | | | | | | | |
| M07 | | | | | | | | | |
| H01 | | | | | | | | | |
| H02 | | | | | | | | | |
| H03 | | | | | | | | | |
| H04 | | | | | | | | | |
| H05 | | | | | | | | | |
| A01 | | | | | | | | | |
| A02 | | | | | | | | | |
| A03 | | | | | | | | | |

**Aggregate Report**

- Overall pass rate: ____%
- Avg Context Recall: ____
- Avg Context Precision: ____
- Avg Faithfulness: ____
- Avg Relevance: ____
- Avg Completeness: ____
- Failure type distribution: ____

**Ba cases có Overall Score thấp nhất**

1. ID: ____ | Score: ____ | Failure type: ____
2. ID: ____ | Score: ____ | Failure type: ____
3. ID: ____ | Score: ____ | Failure type: ____

**Nhận xét ngắn:** Metric nào yếu nhất? Kết quả gợi ý vấn đề nằm ở retrieval
hay generation?

> *Câu trả lời:*

### Exercise 3.3 — LLM-as-a-Judge Rubric Design

Thiết kế rubric domain-specific cho OrbitTech Customer Support. Mỗi mức phải
đủ cụ thể để hai người chấm độc lập có thể hiểu giống nhau.

Chọn 3–5 dimensions:

- [ ] Correctness
- [ ] Completeness
- [ ] Relevance
- [ ] Evidence/citation
- [ ] Actionability
- [ ] Safety/privacy
- [ ] Tone/clarity
- [ ] Dimension khác: __________

| Score | Tiêu chí domain-specific | Ví dụ response |
|---:|---|---|
| 5 | | |
| 4 | | |
| 3 | | |
| 2 | | |
| 1 | | |

**Ba edge cases khó chấm**

| Edge Case | Tại sao khó chấm? | Rubric xử lý thế nào? |
|---|---|---|
| | | |
| | | |
| | | |

**Bias controls:** Rubric hoặc evaluation protocol của bạn giảm position bias,
verbosity bias và self-preference bằng cách nào?

> *Câu trả lời:*

### Exercise 3.4 — Framework Comparison (Bonus +10)

Chỉ làm sau khi hoàn thành 3.1–3.3. Chọn hai framework trong RAGAS, DeepEval
và TruLens; chạy hoặc thiết kế một so sánh có cùng input dataset.

| Tiêu chí | Framework 1: ____ | Framework 2: ____ |
|---|---|---|
| Setup complexity | | |
| Metrics available | | |
| CI/CD integration | | |
| Kết quả trên cùng dataset | | |
| Insight rút ra | | |

- Scores có nhất quán không?
- Framework nào strict hơn và vì sao?
- Hai framework có tìm ra cùng failure cases không?

> *Phân tích:*

### Exercise 3.5 — Retrieval Reranking (Bonus +5)

Mục tiêu: kiểm tra việc đổi thứ tự chunks có tăng Context Precision mà không
thay đổi Context Recall hay không.

1. Chọn ít nhất 5 cases từ `artifacts/actual_answers.json`.
2. Tính Context Recall và Context Precision trước rerank.
3. Implement `rerank_by_overlap()` hoặc một reranker khác.
4. Rerank cùng tập chunks, không thêm hoặc xóa chunk.
5. Tính lại hai metrics và giải thích kết quả.

| ID | Recall before | Recall after | Precision before | Precision after | Delta Precision |
|---|---:|---:|---:|---:|---:|
| | | | | | |
| | | | | | |
| | | | | | |
| | | | | | |
| | | | | | |
| **Avg** | | | | | |

**Tại sao Recall dự kiến không đổi?**

> *Câu trả lời:*

**Khi nào reranking không đủ và cần sửa retriever/query/chunking?**

> *Câu trả lời:*

---

## Part 4 — Reflection (16:35–16:50)

Hoàn thành `reflection.md` bằng kết quả thật từ Exercise 3.2.

---

## Completion Checklist

Hoàn thành kiểm tra cuối trong khoảng 16:50–17:00.

- [ ] Tất cả required tests pass.
- [ ] `golden_dataset.json` validate thành công.
- [ ] Exercise 3.1 hoàn thành trong file JSON và bảng kết quả phía trên.
- [ ] Exercise 3.2 có năm metrics, aggregate report và ba cases thấp nhất.
- [ ] Exercise 3.3 có rubric 1–5 và bias controls.
- [ ] `reflection.md` có ba failure analyses và regression strategy.
- [ ] Đã copy `template.py` thành `solution/solution.py`.
- [ ] Exercise 3.4 và 3.5 chỉ làm nếu chọn bonus.
