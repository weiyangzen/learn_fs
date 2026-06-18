# sources/object-store/garage/src/garage/tests/k2v/batch.rs

Purpose: This K2V integration test exercises batch insertion, range search, pagination markers, reverse scans, prefix filtering, concurrent values, tombstones, and batch deletion through raw signed K2V HTTP requests.

Important APIs and types: `test_batch` uses `CustomRequester`, Hyper methods/statuses, `serde_json::json`, `assert_json_diff::assert_json_eq`, base64 encoding, `json_body`, and K2V query modes `search` and `delete`. It tracks causality tokens in a `HashMap`.

Control flow: The test creates a bucket, posts an insert batch of six items, reads each item back to capture causality tokens, then posts multiple search operations in one request covering full range, start/end, reverse, limit, and prefix. It updates selected items with and without causality tokens to create deletion, replacement, and conflict states, searches again, deletes ranges/prefixes in batch, refreshes tombstone tokens, and finally searches normal/reverse/tombstone-inclusive views.

State and persistence behavior: The test persists K2V entries under partition key `root` and multiple sort keys. It validates causality-token-driven overwrite versus concurrent insertion, null values as tombstones, range deletion counts, `more`/`nextStart`, and base64-encoded value arrays.

Dependencies and integration points: It integrates the K2V API server, bucket permissions, request signing, JSON protocol shape, causality metadata, and underlying K2V table/index behavior.

Risks: Expected JSON is very detailed and can be brittle if field names, default booleans, ordering, or pagination semantics change. It assumes deterministic sort order and immediate visibility after writes.

Test signals: Strong signals include 204 batch insert/update, exact read bodies and causality headers, exact batch search JSON for range/prefix/reverse/limit cases, delete counts, tombstone representation as `null`, and omission of tombstones from default search.
