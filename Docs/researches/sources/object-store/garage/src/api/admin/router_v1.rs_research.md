## sources/object-store/garage/src/api/admin/router_v1.rs

Purpose: declares v1 admin endpoints, parses `/v1/...` routes, and provides a compatibility bridge from selected v0 endpoints.

Important APIs/types/functions: `Endpoint` is v0-like but `GetKeyInfo` adds `show_secret_key`. `Endpoint::from_request<T>` parses `/v1/...` paths. `Endpoint::from_v0` maps compatible `router_v0::Endpoint` variants into v1, injecting `show_secret_key: Some("true")` for legacy key-info behavior.

Control flow: route parsing mirrors v0 with `/v1/` prefixes. Compatibility mapping explicitly permits endpoints whose request/response semantics remained compatible and rejects others with `Error::bad_request("v0/ endpoint is no longer supported...")`.

State/persistence: none.

Dependencies/integration: used by `router_v2.rs::AdminApiRequest::from_v1` for v1-to-v2 compatibility. Relies on the common router macros and admin error type.

Risks: compatibility is manually curated. Any endpoint listed as compatible must preserve body syntax and response semantics expected by old clients. `showSecretKey` is parsed as a string in v1 and later interpreted as `== "true"`, so other truthy strings are false.

Test signals: no local tests. The main signal is compiler coverage of enum matches and integration coverage through compatibility endpoints.
