## sources/object-store/garage/src/api/k2v/batch.rs

Purpose: implements K2V batch insert/read/delete and range-poll handlers.

Important APIs/types/functions: `handle_insert_batch`, `handle_read_batch`, `handle_delete_batch`, `handle_poll_range`, private query handlers, and JSON structs `InsertBatchItem`, `ReadBatchQuery/Response/Item`, `DeleteBatchQuery/Response`, `PollRangeQuery/Response`.

Control flow: insert batch parses JSON, decodes optional base64 values, maps absent value to tombstone, parses causality tokens, and calls `k2v.rpc.insert_batch`. Read batch runs queries concurrently with `join_all`; single-item mode forbids range params and direct-gets one sort key, otherwise uses `read_range`. Delete batch either deletes a single matched item with its causal context or range-deletes all non-tombstones using batch insert of deleted values. Poll range parses body, clamps timeout to 1-600 seconds, calls subscription RPC, returns changed items/marker or `304`.

State/persistence: writes K2V values/tombstones through RPC and reads item table ranges. Batch delete mutates many sort keys in a partition.

Dependencies/integration: uses K2V model item table, causality parser from `item.rs`, common JSON/body helpers, and `range::read_range`.

Risks: batch read has unbounded query count in the body. Non-single delete reads all matching items with no explicit limit, which can be expensive. Values are base64 JSON strings; invalid base64 is client error.

Test signals: no local tests. Integration should cover conflict/tombstone handling, range pagination, and long polling.
