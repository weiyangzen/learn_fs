# sources/user-network-fs/samba/source3/rpc_server/rpc_handles.c

Purpose: implements source3 policy-handle compatibility helpers on top of the DCE/RPC core handle API and provides a pipe access check for anonymous restrictions.

Important APIs and functions: `check_open_pipes()` and `num_pipe_handles()` expose a global handle count. `create_policy_hnd()` creates a `dcesrv_handle`, attaches a tiny destructor object that decrements `num_handles`, moves optional talloc-owned service data into the handle, writes the wire handle, and increments the count. `_find_policy_by_hnd()` wraps lookup and returns typed private data with NTSTATUS. `close_policy_hnd()` validates and frees the core handle. `pipe_access_check()` enforces `restrict anonymous > 0` by requiring completed auth and at least `SECURITY_USER`, except schannel-authenticated calls are accepted.

Control flow: server stubs create policy handles during open/connect operations, retrieve private state on later opnums, and close handles on close calls. Lookup intentionally avoids passing the requested handle type to `dcesrv_handle_lookup()` so type mismatch can return NULL without setting a fault in `pipes_struct`; empty or missing handles set context mismatch.

State and persistence: `num_handles` is static process state. Handle-private data is owned by the DCE/RPC handle via talloc and freed when the handle is freed. There is no disk persistence.

Dependencies: generated NDR policy handle helpers, DCE/RPC core, Samba auth/session/security levels, loadparm `restrict anonymous`, and tsocket/security headers used by the surrounding RPC stack.

Risks: `num_handles` is process-global and not synchronized; it assumes the server execution model does not need cross-thread atomicity. Moving `data_ptr` transfers ownership, so callers must not reuse it after successful creation. Anonymous restriction enforcement depends on `auth_finished` and session user level correctness.

Test signals: tests should cover empty handle lookup, invalid handle lookup, handle type mismatch, private-data lifetime on close, count increments/decrements, schannel bypass, and anonymous denial when `restrict anonymous` is enabled.
