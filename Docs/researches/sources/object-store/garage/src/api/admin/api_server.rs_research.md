# sources/object-store/garage/src/api/admin/api_server.rs

Purpose: implements the Admin API HTTP/RPC server, endpoint parsing, request dispatch, bearer-token authorization, and node matching for proxied local requests.

Important APIs/types: `AdminRpc` carries proxied public or local admin requests. `AdminRpcResponse` carries tagged success or serialized API errors. `AdminApiServer::new` initializes hashed configured tokens and registers the RPC endpoint. `run` starts the generic API server. `handle_http_api` parses old/new routes, determines authorization type, verifies bearer tokens, and dispatches special or JSON endpoints. `verify_authorization` validates config tokens or persisted admin-token-table entries using Argon2. `find_matching_nodes` resolves `self`, `*`, or node ID prefixes.

Control flow and state: configured admin/metrics tokens are hashed at startup and kept in memory. Persisted token lookup is local table state keyed by token prefix and filtered for non-expired scope-bearing records. HTTP paths under `/v0/` and `/v1/` use legacy routers; other paths use new request parsing. RPC handling converts handler errors into transportable HTTP code/error/message triples.

Dependencies/integration: uses `garage_api_common::generic_server`, Hyper requests/responses, Garage RPC endpoint machinery, admin routers, argon2 password hashing, Garage system node state, background runner, optional Prometheus exporter, and admin schema/handlers.

Risks: startup hashes configured tokens with random salts, so equality uses Argon2 verification rather than stable hashes. `parse_authorization` requires exact `Bearer ` prefix. Global config tokens have no prefix; table tokens must be `prefix.secret`. `GetCurrentAdminTokenInfo` is deliberately exempted from scope checks after token validity. Node-prefix matching errors on zero or multiple matches.

Test signals: legacy and new route parsing, CORS headers on success/error, missing/malformed bearer headers, config token and table token verification, expired/scope-denied tokens, metrics token requirement modes, RPC error marshalling, and node selector behavior for `self`, `*`, unique and ambiguous prefixes.
