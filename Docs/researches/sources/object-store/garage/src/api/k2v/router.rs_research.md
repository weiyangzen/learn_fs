## sources/object-store/garage/src/api/k2v/router.rs

Purpose: parses HTTP K2V API requests into typed endpoint variants and declares endpoint authorization requirements.

Important APIs/types/functions: `Endpoint` enum, `Endpoint::from_request`, method parsers `from_get/from_search/from_post/from_put/from_delete`, `get_partition_key`, `get_sort_key`, `authorization_type`, and generated query parameters.

Control flow: path first segment is bucket name; remainder is URL-decoded partition key. `OPTIONS` returns early. GET with partition key reads/polls item; GET without key reads index. SEARCH and POST keyword variants map to batch or poll-range operations. PUT inserts item requiring `sort_key`; DELETE deletes item. Query macro parses keywords `delete`, `search`, `poll_range` and fields like `prefix`, `start`, `sort_key`, `timeout`.

State/persistence: none.

Dependencies/integration: used by `K2VApiServer::parse_endpoint`; uses common router macros and authorization enum.

Risks: custom HTTP method `SEARCH` is supported through `Method::from_bytes`. Path splitting treats empty partition key as no-key operation. Unknown methods and malformed UTF-8 are bad requests. Authorization mapping marks read-only endpoints as read and everything else as write.

Test signals: no local tests; route matrix should be integration-tested.
