# sources/object-store/garage/src/api/admin/api.rs

Purpose: defines the public and RPC-serializable Admin API request/response schema for cluster, token, layout, key, bucket, node, worker, and block operations.

Important APIs/types: `admin_endpoints!` generates `AdminApiRequest`, `AdminApiResponse`, and tagged RPC responses for all public endpoints. `local_admin_endpoints!` creates multi-node wrappers for local operations and `LocalAdminApiRequest/Response`. Data contracts include `MultiRequest/MultiResponse`, cluster status/health/statistics structures, admin token and access key structures, layout role and history structures, bucket info/update/inspection structures, node statistics, worker state, block errors, block backlinks, and purge responses.

Control flow and state: this file mostly has schema declarations; generated `RequestHandler` impls delegate actual work to per-domain modules. Multi-node request handlers use `find_matching_nodes`, Garage RPC `call_many`, and tagged local responses to aggregate successes and errors by node ID.

Dependencies/integration: integrates serde serialization, utoipa schema generation, `garage_rpc` RPC helpers, `garage_api_common` XML/common-error types, admin macros, and all domain handler modules. Compatibility is visible through many `FIXME for v3` optional/default fields kept for v2 clients.

Risks: schema changes are public API changes. Untagged enums such as preview results, bucket alias changes, retry block requests, and admin responses can be ambiguous if fields overlap. Multi-node response conversion must match the local response variant or reports "returned invalid value". The endpoint list must stay synchronized with routers, OpenAPI generation, auth scopes, and handler impls.

Test signals: schema serialization/deserialization round trips, OpenAPI generation, router-to-request parsing, tagged RPC conversions, multi-node aggregation with success/error/mismatched variants, backward compatibility for defaulted fields, and scope names matching `AdminApiRequest::name`.
