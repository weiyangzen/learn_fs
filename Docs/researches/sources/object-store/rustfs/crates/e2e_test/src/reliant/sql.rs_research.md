# sources/object-store/rustfs/crates/e2e_test/src/reliant/sql.rs

## sources/object-store/rustfs/crates/e2e_test/src/reliant/sql.rs

Purpose: ignored live-server tests for S3 SelectObjectContent over CSV and JSON objects. The suite checks basic filtering, projected output, limit/order behavior, and failure modes.

Important APIs and functions: `create_aws_s3_client` and `setup_test_bucket` provide local S3 setup. `upload_test_csv` and `upload_test_json` write deterministic fixture objects. `process_select_response` drains the AWS SDK `SelectObjectContentOutput` event stream, concatenating `Records` payload bytes until `End` and ignoring stats/progress/continuation events.

Control flow: CSV tests upload the fixture, build `InputSerialization::csv` with `FileHeaderInfo::Use`, build default CSV output serialization, call `select_object_content`, and inspect the concatenated record text. The basic test filters `age > 28`; the aggregation-named test projects `name, age` for `age >= 25`; the limit test expects exactly two non-empty output lines; the order-by test checks the top two age records. The JSON test uses `JsonInput` of type `Document`, projects fields from alias `s`, and checks matching names/ages. Error tests assert SDK send failure for an invalid column and nonexistent object.

State and persistence: fixture objects persist in `test-sql-bucket` under fixed keys. Tests are serial but do not clean up, so later runs overwrite the same fixtures. Select processing is streaming and does not persist state.

Dependencies and integration points: AWS SDK S3 select-object types, RustFS select SQL parser/executor, event-stream framing, CSV/JSON input and output serializers, Tokio multi-thread runtime, and `serial_test`.

Risks: ignored by default and requires a live server with S3 Select support. Assertions use substring matching and do not fully validate row order or exact serialization for most tests. `JsonType::Document` is used with newline-delimited JSON-like content, which may depend on RustFS interpretation. Error handling only checks that failures occur, not exact error codes.

Test signals: validates end-to-end select query execution and event-stream decoding for common CSV/JSON paths plus invalid-query and missing-object failure paths.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/e2e_test/src/reliant/sql.rs -->
