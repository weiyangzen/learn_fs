# sources/user-network-fs/libsmb2/lib/smb2-share-enum.c

## Purpose
Implements asynchronous share enumeration through DCERPC SRVSVC `NetrShareEnum` over an existing SMB2 connection.

## Important APIs, Types, And Functions
The exported API is `smb2_share_enum_async`. Internal callbacks are `share_enum_bind_cb`, `srvsvc_ioctl_cb`, and `nse_free`. The private state container `struct smb2nse` stores the user callback and `srvsvc_NetrShareEnum_req`.

## Control Flow
`smb2_share_enum_async` creates a DCERPC context from the SMB2 context, allocates request state, builds a `\\server` name from `smb2->server`, sets the requested info level and maximum length, then starts an async bind to the `srvsvc` pipe/interface. On bind success, `share_enum_bind_cb` issues the `SRVSVC_NETRSHAREENUM` call. `srvsvc_ioctl_cb` forwards either transport status or returned SRVSVC status to the original callback and destroys the DCERPC context.

## State And Persistence
The outstanding operation state is `struct smb2nse`, freed on every callback completion/error path. The server name string is owned by the request state. DCERPC context lifetime is scoped to this one enumeration.

## Dependencies And Integration Points
Depends on libsmb2 DCERPC helpers, generated SRVSVC coders, raw SMB2 context access, and callback conventions that use `smb2_command_cb`.

## Risks
The server string allocation uses `strlen(smb2->server) + 3`, sufficient for two backslashes plus NUL, but assumes `smb2->server` is set. Callback status mixes SMB transport status and SRVSVC application status, so callers must interpret both. There is no pagination loop for `ResumeHandle`; it requests `0xffffffff` bytes and returns the first server response.

## Test Signals
Mock bind failure, DCERPC call failure, SRVSVC non-success status, null/empty server names, multiple info levels, large share lists requiring resume handles, and callback/data lifetime after completion.
