# sources/user-network-fs/samba/source4/smb_server/smb/reply.c

## Purpose
Contains most SMB1 command handlers. It translates individual SMB wire commands into Samba raw/NTVFS operation unions, validates request shapes and handles, invokes backends synchronously or asynchronously, and serializes command-specific SMB replies including AndX continuations, raw reads, session setup replies, tree disconnects, logoff/exit cleanup, and NetBIOS session packets.

## Important APIs, Types, And Functions
- Generic send helpers such as `reply_simple_send()`, `reply_tcon_send()`, and per-operation async callbacks consume NTVFS results and call `smbsrv_send_reply()`.
- Tree/session functions: `smbsrv_reply_tcon`, `smbsrv_reply_tcon_and_X`, `smbsrv_reply_sesssetup`, `smbsrv_reply_sesssetup_send`, `smbsrv_reply_ulogoffX`, and `smbsrv_reply_exit`.
- File operations: open/create/temp/NTCreateX, read/readX/readbraw, write/writeX/writeclose, close/flush/seek, lock/unlock/lockingX, getattr/setattr/getattrE/setattrE, unlink, mkdir/rmdir, rename/copy.
- Print and legacy commands: `SMBsplopen`, `SMBsplwr`, `SMBsplclose`, `SMBsplretq`, `SMBreadBmpx`, `SMBwriteBmpx`, `SMBwriteBs`.
- `smbsrv_reply_ntcancel()` scans pending requests and invokes `ntvfs_cancel()`.
- `smbsrv_reply_special()` handles NBT session request and keepalive packets.

## Control Flow
Handlers follow a consistent pattern: check word count, allocate `req->io_ptr`, parse VWV/data fields with endian macros and request helpers, create an NTVFS request with `SMBSRV_SETUP_NTVFS_REQUEST`, validate file handles with `smbsrv_pull_fnum()`, then call the appropriate NTVFS backend. Async callbacks inspect backend status, build a reply with `smbsrv_setup_reply()`, push fields, and send or chain. AndX handlers set `SMB_CHAIN_NONE` placeholders and finish through `smbsrv_chain_reply()`. `readbraw` is special: it sends only an NBT header plus raw bytes and must complete synchronously. Session setup parsing is split by WCT into old, NT1, and SPNEGO variants, then delegated to `sesssetup.c`.

## State And Persistence
Successful opens create persistent SMB handles through the NTVFS handle callbacks configured on the tcon. `req->chained_fnum` lets chained operations reuse the just-opened FID. `tdis` destroys all handles under a tree and frees the tcon. `exit` destroys handles for the request PID and notifies all tcon backends. `ulogoffX` destroys all session handles, calls backend logoff, frees the session, and prevents chained reuse. NBT session request parsing stores called/calling names in negotiation state.

## Dependencies And Integration Points
Uses almost every NTVFS frontend operation: connect, open, close, read, write, lock, seek, flush, fsinfo, path/file info, mkdir, rmdir, rename, copy, ioctl, lpq, search close, exit, logoff, and cancel. Integrates with `service.c` for tree setup, `sesssetup.c` for authentication, `request.c` for buffer/string/error/send helpers, `srvtime.c` for DOS time conversion, and `receive.c` for dispatch/chaining.

## Risks
This file is broad and wire-exposed. Each handler's WCT, offset, length, and block-type validation is significant. Some legacy paths return placeholder statuses such as `NT_STATUS_FOOBAR` and `ERRuseSTD`, which are compatibility-sensitive. Raw reads bypass SMB signing and normal SMB headers by design. Chained open/NTCreateX handle propagation depends on `req->chained_fnum`. `ntcancel` matches pending requests by TID/UID/MID/PID and sends no reply. Cleanup paths have TODOs for canceling pending requests, so async operations during logoff/tree disconnect are a risk area.

## Test Signals
Test representative command families rather than every opcode only through unit tests: tree connect AndX followed by chained command, session setup variants, NTCreateX with Unicode alignment, raw read success/failure, readX/writeX large counts and 64-bit offsets, malformed data block lengths, handle/session ownership rejection, lockX large-file lock arrays, tdis/logoff/exit cleanup, print queue truncation to max transmit, NBT session request/keepalive behavior, and backend async vs sync completion.
