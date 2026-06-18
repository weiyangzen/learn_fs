## sources/object-store/garage/src/api/admin/router_v2.rs

Purpose: parses the current v2 admin API into typed `AdminApiRequest` values and provides selected v1 compatibility mapping.

Important APIs/types/functions: `AdminApiRequest::from_request` uses `router_match!(@gen_path_parser_v2 ...)` to parse method/path/query/body into typed request wrappers. `AdminApiRequest::from_v1` maps compatible `router_v1::Endpoint` values by parsing legacy JSON bodies into v2 request types. `authorization_type` classifies requests as public, metrics-token, or admin-token.

Control flow: special non-`/v2/` paths `/check`, `/health`, `/metrics`, and any `OPTIONS` are matched first. Other paths are generated from v2 operation names such as `/v2/GetClusterStatus`. Parameter modes include empty request structs, whole JSON body, JSON body plus query field, bearer-token extraction for `GetCurrentAdminTokenInfo`, query defaults, and parsed booleans.

State/persistence: none directly; it constructs requests that handlers later execute against cluster state.

Dependencies/integration: central bridge between hyper requests and `crate::api::*` request types. Uses common helpers for JSON body parsing, admin `Authorization`, and router macros.

Risks: the macro-driven mapping must stay in sync with OpenAPI and handler impls. Compatibility intentionally excludes changed delete semantics and changed layout/status/update endpoints. Public authorization for `CheckDomain` and `Health` is explicit; adding sensitive endpoints to that arm would be a security bug.

Test signals: no local tests. Compile-time type construction catches many request-shape mismatches; route behavior should be covered at API/integration level.
