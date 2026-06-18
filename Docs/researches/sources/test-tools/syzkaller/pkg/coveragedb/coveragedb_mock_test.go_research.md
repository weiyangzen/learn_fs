# sources/test-tools/syzkaller/pkg/coveragedb/coveragedb_mock_test.go

Purpose: tests `SaveMergeResult` persistence behavior using generated Spanner client mocks.

Important APIs/types/functions: `spannerMockTune` and `TestSaveMergeResult`.

Control flow: table-driven cases feed empty/wrong JSONL, one merged coverage record, one function-lines record, two records, and 2000 records. Mock expectations verify `Apply` call counts and mutation batch sizes, including two 1000-record batches plus one history-only batch for 2000 inputs.

State and persistence: no real Spanner writes; mocks record calls.

Dependencies and integration: uses `coveragedb/mocks.SpannerClient`, Spanner mutation types, `json.Decoder`, and testify mock matchers.

Risks: mutation content is not inspected beyond count. Empty JSON object is expected to error because `JSONLWrapper` has neither `MCR` nor `FL`.

Test signals: good signal for batching, wrapper validation, row-count accounting, and nil/wrong JSON paths in the persistence ingestion flow.
