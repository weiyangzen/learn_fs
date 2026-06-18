# sources/user-network-fs/samba/source4/rpc_server/common/forward.c

Purpose: implements the common async forwarding bridge used by RPC server methods that delegate work to another Samba task over IRPC. The only exported entry point is `dcesrv_irpc_forward_rpc_call()`.

Important APIs and control flow: `dcesrv_irpc_forward_rpc_call()` checks that the incoming `dcesrv_call_state` permits async replies, resolves a named IRPC binding handle with `irpc_binding_handle_by_name()`, applies the caller security token to the IRPC handle, sends the NDR call by `dcerpc_binding_handle_call_send()`, marks the call with `DCESRV_CALL_STATE_FLAG_ASYNC`, and registers `dcesrv_irpc_forward_callback()`. The callback receives the IRPC completion, maps failures to `DCERPC_FAULT_CANT_PERFORM`, frees the subrequest, then calls `_dcesrv_async_reply()`.

State and persistence: no persistent storage. Runtime state is the talloc-owned `dcesrv_forward_state`, the pending tevent request, and mutations of `dce_call->state_flags` and `fault_code`.

Dependencies and integration: depends on tevent, generated DCE/RPC NDR tables, Samba messaging/IRPC, auth session info, and `dcesrv_imessaging_context()`. Used by DRSUAPI to forward replication and KCC operations to `dreplsrv` or `kccsrv`.

Risks and test signals: callers that cannot do async receive a fault. Failures in binding, allocation, security-token transfer, or send are reported as generic DCE/RPC faults, so tests should verify async vs sync caller behavior, timeout propagation, security token forwarding, and callback reply completion.
