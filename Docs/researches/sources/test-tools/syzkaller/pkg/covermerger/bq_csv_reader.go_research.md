# sources/test-tools/syzkaller/pkg/covermerger/bq_csv_reader.go

Purpose: exports raw namespace coverage rows from BigQuery to GCS as gzipped CSV shards and exposes them as one concatenated reader.

Important APIs/types/functions: `InitNsRecords`, `initGCSMultiReader`, `gcsGZIPMultiReader`, `Read`, and `Close`.

Control flow: `InitNsRecords` validates namespace, file path, and optional commit, creates a BigQuery client, exports grouped coverage rows for a date range to `gs://syzbot-temp/bq-exports/<uuid>/*.csv.gz`, waits for job completion, then returns a GCS multi-reader. `initGCSMultiReader` lists exported objects. `Read` lazily opens each GCS file, wraps it in gzip, reads until EOF, closes it, and advances to the next file. `Close` closes the current gzip and file readers.

State and persistence: creates temporary GCS export objects and reads them; no cleanup is visible here. Reader state tracks remaining paths and current readers.

Dependencies and integration: BigQuery, GCS client abstraction, validators, UUID, and civil dates. Used by `cover.GetMergeResult` and historical merge jobs.

Risks: SQL is built with `fmt.Sprintf`; validation mitigates namespace/file/commit but date and namespace still influence table/query strings. Temporary GCS exports are not deleted. GCS object ordering follows list order and may affect CSV header repetition handling. BigQuery client is not closed.

Test signals: `bq_csv_reader_test.go` focuses on the multi-gzip reader, including corrupt shard behavior.
