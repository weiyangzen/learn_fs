# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_opipe.c

## Purpose

`smb_opipe.c` implements the SMB server's named-pipe bridge for IPC shares. It maps SMB message pipe opens, reads, writes, ioctl/FSCTL operations, and synthetic attributes onto AF_UNIX sockets under `SMB_PIPE_DIR`, allowing in-kernel SMB request handling to communicate with userland NDR/RPC pipe services.

## Main Interfaces

- `smb_opipe_open()` allocates an `smb_opipe_t`, connects to the named pipe service, sends authenticated user/client metadata, and installs the pipe on an SMB ofile.
- `smb_opipe_close()` shuts down and closes the underlying socket when the ofile closes.
- `smb_opipe_write()` and `smb_opipe_read()` move request/response bytes between SMB uios and the socket.
- `smb_opipe_ioctl()` forwards ioctl operations such as `FIONREAD`.
- `smb_opipe_getattr()` and `smb_opipe_getname()` provide synthetic pipe metadata.
- `smb_opipe_fsctl()` dispatches SMB2 named-pipe FSCTLs, with `FSCTL_PIPE_TRANSCEIVE` handled by `smb_opipe_transceive()` and `FSCTL_PIPE_WAIT` handled by `smb_opipe_wait()`.
- `smb_opipe_dealloc()` frees pipe state and closes a still-attached socket in open error paths.

## Behavior And Data Flow

Open handling creates a socket with the request credential, normalizes names such as `\PIPE\foo` to lowercase `foo`, connects to `${SMB_PIPE_DIR}/foo`, then sends an XDR-encoded `smb_netuserinfo_t` preceded by `smb_pipehdr_t`. The pipe service replies with an NT status, so access checks can be delegated to the service.

Pipe reads are intentionally single `recvmsg` calls: if no data is available they block, but they do not loop to fill the whole buffer. Pipe writes loop until the caller's uio is drained or the socket errors. Both take a socket hold under `p_mutex` so concurrent close can null `p_socket` safely while active I/O completes.

Blocking user-info exchange and pipe reads integrate with request cancellation. The request is moved to `SMB_REQ_STATE_WAITING_PIPE`, `cancel_method` is set to `smb_opipe_cancel`, and disconnect/termination can wake blocked socket reads by shutting down the socket. The cancellation path waits out `SMB_REQ_STATE_CANCEL_PENDING` before restoring state.

`FSCTL_PIPE_TRANSCEIVE` decodes input into an SMB VDB, writes it to the pipe, allocates mbufs for the response, reads once, attaches the mbuf to the FSCTL output, and approximates `NT_STATUS_BUFFER_OVERFLOW` by checking whether the output buffer filled and `FIONREAD` says more data remains.

## Dependencies

This file depends on illumos kernel socket APIs, SMB request/ofile/tree state, request-specific memory, SMB mbuf chains, XDR helpers from `smb_xdr.h`, `smb_user_netinfo_*`, and Windows named-pipe FSCTL constants from `smb/winioctl.h`.

## Notable Invariants And Risks

- `smb_opipe_t` objects are protected by `SMB_OPIPE_MAGIC`; socket lifetime is protected by `p_mutex` plus `ksocket_hold/rele`.
- `smb_opipe_cancel()` only shuts down the socket for session disconnect or termination, not normal SMB cancel requests.
- A blocked pipe operation can make the socket unusable after cancellation, so the logic is intentionally limited to teardown paths.
- `smb_opipe_open()` checks `smb_tree_is_connected()` after connect/userinfo because tree disconnect may race with slow pipe service startup.
- `smb_opipe_wait()` does not truly wait for pipe instance availability; it verifies existence and optionally delays briefly.
