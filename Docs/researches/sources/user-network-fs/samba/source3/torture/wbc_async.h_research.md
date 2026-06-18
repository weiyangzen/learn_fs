<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/torture/wbc_async.h -->
# sources/user-network-fs/samba/source3/torture/wbc_async.h

## Purpose
`wbc_async.h` is the public interface for the asynchronous winbind client helper used by Samba torture code and related async wbclient wrappers.

## Important APIs, types, and functions
- `enum wbcDebugLevel` defines fatal, error, warning, and trace levels.
- `wb_context_init()` creates the reusable transport context.
- `wb_trans_send()` and `wb_trans_recv()` provide the generic async winbind request/response primitive with optional privileged-pipe access.
- `wbcSetDebug()`, `wbcSetDebugStderr()`, and `wbcDebug()` control debug output.
- Error helpers expose `map_wbc_err_from_errno()`, `tevent_req_is_wbcerr()`, and `tevent_req_simple_recv_wbcerr()`.
- The header declares async wrappers for SID/UID/GID mapping, authentication, name/SID lookup, ping, interface version/details, netbios/domain names, and domain info.

## Control flow
The send/recv declarations follow tevent conventions: allocate a request with `_send`, drive the event loop, then call the matching `_recv` to collect outputs and a `wbcErr`. Higher-level async functions are layered on top of `wb_trans_send()`.

## State and persistence behavior
`struct wb_context` is opaque to callers. The header implies callers own output memory through talloc contexts passed to receive functions. No persistent state is declared.

## Dependencies and integration points
The header includes talloc, tevent, `nsswitch/libwbclient/wbclient.h`, and `nsswitch/wb_reqtrans.h`. It bridges Samba's tevent style with libwbclient data types such as `wbcDomainSid`, `wbcAuthUserParams`, `wbcDomainInfo`, and `winbindd_response`.

## Risks and edge cases
- All APIs depend on correct tevent loop ownership and matching send/recv calls.
- The transport can require privileged pipe access for some operations; callers must set `need_priv` correctly in generic transactions or use higher-level wrappers.
- Debug callbacks receive a `va_list` and must obey the printf attribute contract.

## Test signals
Compile-time interface conformance and successful async wbclient torture tests validate the header. Error helper tests should confirm tevent errors map to stable `wbcErr` values.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/torture/wbc_async.h -->
