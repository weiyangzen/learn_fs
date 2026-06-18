## sources/object-store/garage/src/api/k2v/item.rs

Purpose: implements single-item K2V read/insert/delete/poll operations and content negotiation.

Important APIs/types/functions: `X_GARAGE_CAUSALITY_TOKEN`, `ReturnFormat::{Json,Binary,Either}`, `parse_causality_token`, `ReturnFormat::{from, make_response, make_binary_response, make_json_response}`, `handle_read_item`, `handle_insert_item`, `handle_delete_item`, and `handle_poll_item`.

Control flow: reads fetch an item from `k2v.item_table`, choose response format from `Accept`, and return binary, JSON base64 array, conflict status, no-content tombstone, or `NoSuchKey`. Inserts/deletes parse optional causality token header and write value/tombstone through `k2v.rpc.insert`. Poll parses query causality token, clamps timeout to 1-600 seconds, calls `rpc.poll_item`, and returns item response or `304 Not Modified`.

State/persistence: writes K2V values/tombstones and reads K2V item table. Causality contexts preserve conflict resolution semantics.

Dependencies/integration: used by API server dispatch; depends on K2V DVVS model, common body helpers, and K2V error mappings.

Risks: insert collects entire body in memory. Binary reads with conflicts return `409` with only causality token and empty body, requiring clients to retry with JSON. Accept parsing is simple comma trimming and does not parse q-values.

Test signals: no local tests; needs API tests for content negotiation, causality conflict cases, tombstones, and polling.
