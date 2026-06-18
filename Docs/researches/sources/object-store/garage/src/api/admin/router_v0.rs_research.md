## sources/object-store/garage/src/api/admin/router_v0.rs

Purpose: declares the legacy v0 admin endpoint enum and request parser.

Important APIs/types/functions: `Endpoint` variants cover special, cluster, layout, key, bucket, bucket-key permission, and bucket alias endpoints. `Endpoint::from_request<T>` parses method, path, and query into an endpoint. `generateQueryParameters!` creates the local `QueryParameters` parser for `id`, `search`, `globalAlias`, `alias`, and `accessKeyId`.

Control flow: `from_request` extracts `uri.path()` and query, builds `QueryParameters`, then uses `router_match!(@gen_path_parser ...)` to match hard-coded `/v0/...` paths and required query fields. It logs unused known query parameters but still returns the parsed endpoint.

State/persistence: none; this is routing-only.

Dependencies/integration: used by compatibility code in `router_v1.rs`, which maps supported v0 requests into v1 equivalents. It depends on `garage_api_common::router_macros`.

Risks: v0 uses older semantics and response shapes. Several routes are differentiated only by required query fields, so duplicated or empty query fields can affect route selection. Unknown query parameters are only debug logged except for duplicate known fields.

Test signals: no file-local tests. Behavior is macro-generated and should be covered by admin compatibility/integration tests if present.
