# sources/object-store/garage/src/api/admin/macros.rs

Purpose: provides code-generation macros that connect endpoint type declarations in `api.rs` to request/response enums, tagged RPC conversion, dispatch, and local multi-node RPC fanout.

Important macros: `admin_endpoints!` generates `AdminApiRequest`, `AdminApiResponse`, `TaggedAdminApiResponse`, endpoint names, response tagging, `From<Request>` conversions, `TryFrom<TaggedAdminApiResponse>` conversions, and `RequestHandler` dispatch. `local_admin_endpoints!` generates `LocalAdminApiRequest/Response`, public multi-node request/response aliases, conversions, fanout `RequestHandler` impls, local endpoint names, and local dispatch.

Control flow and state: generated public dispatch rejects special endpoints outside HTTP, delegates regular endpoints to their request handlers, and wraps responses. Generated local fanout resolves nodes, sends `AdminRpc::Internal` via `call_many`, then fills `MultiResponse.success` or `.error` maps keyed by hex node ID.

Dependencies/integration: relies on `paste`, serde derives available in the expansion context, `find_matching_nodes`, `AdminRpc`, `AdminRpcResponse`, `RequestStrategy::with_priority(PRIO_NORMAL)`, `HashMap`, `hex`, and the `RequestHandler` trait.

Risks: macro expansions hide a large amount of API surface; endpoint ordering and names become auth scope strings and RPC variant names. Untagged public responses need tagged wrappers for RPC to avoid ambiguity. Local fanout treats unexpected response variants as per-node errors, not hard failures. Special endpoints must remain HTTP-only.

Test signals: compile expansion for new endpoints, conversion tests for tagged responses, special endpoint rejection through generic dispatch, local fanout with success/API error/RPC error/wrong variant, and endpoint name stability for authorization scopes.
