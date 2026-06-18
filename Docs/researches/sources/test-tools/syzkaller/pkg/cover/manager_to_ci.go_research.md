# sources/test-tools/syzkaller/pkg/cover/manager_to_ci.go

Purpose: combines per-PC coverage JSON records with CI/manager metadata and writes one JSONL record per coverage item.

Important APIs/types/functions: `CIDetails`, `dbCoverageRecord`, generic `WriteJSLine`, and `WriteCIJSONLine`.

Control flow: `WriteCIJSONLine` embeds `CIDetails` and `CoverageInfo` in a `dbCoverageRecord`, then delegates to `WriteJSLine`. `WriteJSLine` marshals to compact JSON, appends a newline, and writes to the target writer.

State and persistence: no internal state. Persistence is caller-defined through the `io.Writer`, commonly a file, pipe, or upload stream.

Dependencies and integration: uses `CoverageInfo` from `html.go`. This is the bridge from manager coverage output to CI/BigQuery ingestion records matching `coveragedb/bq-schema.json`.

Risks: `Timestamp` is a string rather than `time.Time`, so formatting validation is outside this layer. JSON field order is Go struct order, and tests assert the exact compact output. Write failures include only the wrapped write error.

Test signals: `manager_to_ci_test.go` checks exact output for a sample coverage record and metadata set.
