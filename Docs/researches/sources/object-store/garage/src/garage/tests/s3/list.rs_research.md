# sources/object-store/garage/src/garage/tests/s3/list.rs

Purpose: This file tests S3 object listing and multipart-upload listing semantics, including V1/V2 pagination, delimiters, prefixes, markers, continuation tokens, multipart upload markers, and multi-character delimiters.

Important APIs and types: Tests are `test_listobjectsv2`, `test_listobjectsv1`, `test_listmultipart`, and `test_multichar_delimiter`. They use AWS SDK `put_object`, `list_objects_v2`, `list_objects`, `create_multipart_upload`, and `list_multipart_uploads` with constant key sets.

Control flow: The object tests upload a fixed set of keys, then list with default settings, max keys, one-item pagination loops, delimiter, delimiter plus pagination, prefix, prefix plus delimiter, prefix plus max keys, and marker/start-after edge cases. The multipart test creates uploads for duplicate and nested keys and performs equivalent listing checks using key/upload markers. The multi-character delimiter test uploads nested keys and compares delimiter `/` with delimiter `b/`.

State and persistence behavior: The tests persist objects and incomplete multipart uploads. They validate list response contents, common prefixes, pagination continuation fields, and truncation behavior against stored key order.

Dependencies and integration points: They exercise S3 metadata indexing, object key ordering, delimiter/prefix grouping, ListObjects V1 and V2 differences, multipart upload metadata, and AWS SDK response decoding.

Risks: The comments note AWS SDK prevents some max-key edge cases, so zero or >1000 values are not tested here. V1 delimiter pagination intentionally returns repeated common prefixes because Garage does not optimize prefix skipping, which is compliant but easy to change accidentally.

Test signals: Exact counts for contents/common prefixes, continuation/marker presence, expected first key under constrained prefix, empty results after markers beyond the last key, multipart upload counts, and exact multi-character delimiter prefix results.
