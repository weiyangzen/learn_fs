# sources/user-network-fs/samba/source3/winbindd/wb_lookupuseraliases.c

Purpose: provides an async wrapper for looking up domain-local alias RIDs that contain a set of user/group SIDs.

Important APIs and types: `wb_lookupuseraliases_send/recv`; `struct wb_lookupuseraliases_state` containing the input `wbint_SidArray` and output `wbint_RidArray`.

Control flow: `send` logs the target domain and SIDs, builds a `wbint_SidArray` by borrowing the caller's SID memory via `discard_const_p`, then calls `dcerpc_wbint_LookupUserAliases_send` on the domain child handle. The callback receives both transport and operation result status with `any_nt_status_not_ok`. `recv` exposes `num_aliases` and moves `state->rids.rids` to the caller.

State and persistence: no persistent state; all output is talloc-owned by the request. The input SID array is borrowed, so the caller's SID memory must outlive the async request.

Dependencies and integration points: generated winbind RPC client stubs, `dom_child_handle(domain)`, SID formatting helpers, and the backend method contract represented in `struct winbindd_methods.lookup_useraliases`.

Risks: input lifetime is important because the state stores a non-owning pointer to caller-provided SIDs. Errors collapse transport and result status into one `NTSTATUS`, so tests should cover both. Large SID arrays rely on child RPC limits rather than local chunking.

Test signals: successful alias lookup with multiple SIDs, empty SID list behavior if callers permit it, child transport failure, operation failure, and validation that returned RIDs are moved under the caller's memory context.
