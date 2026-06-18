# File Research: sources/os/linux/linux/fs/smb/client/cifssmb.c

This is the SMB1/CIFS PDU construction and parsing implementation for the Linux CIFS client. It builds wire requests, sends them through the CIFS transport helpers, decodes SMB/Trans2/NT Transact responses, updates per-tree statistics, and coordinates retry/reconnect behavior.

Primary responsibilities:
- SMB1 negotiation, tree connect/disconnect, echo, and logoff.
- Path and handle operations: create/open, delete, mkdir/rmdir, rename, hard link, symlink, close, flush.
- Sync and async read/write using `SMB_COM_READ_ANDX` and `SMB_COM_WRITE_ANDX`, including NetFS subrequest completion callbacks.
- Byte-range locks, POSIX locks, oplock release signaling.
- Query/set metadata through legacy SMB, Trans2, NT Transact, Unix extensions, POSIX ACLs, CIFS ACLs, DFS referrals, reparse points, filesystem info, extended attributes.
- Conditional code for `CONFIG_CIFS_POSIX`, `CONFIG_FS_POSIX_ACL`, `CONFIG_CIFS_XATTR`, and DFS upcall support.

Important control flow:
- `cifs_reconnect_tcon()` is the gate before most tree-based operations. It waits for server reconnect, serializes session setup with `session_mutex`, can swap alternate passwords after auth failures, reconnects the tree, resets Unix caps, and returns `-EAGAIN` for handle-based commands that cannot safely reuse stale FIDs.
- `small_smb_init()`, `smb_init()`, `smb_init_no_reconnect()`, and `smb_init_nttransact()` are the main request-buffer constructors. They assemble SMB headers, assign stats, and choose small vs large CIFS buffers.
- Many request routines follow the pattern `init -> encode pathname/params/data -> SendReceive/SendReceive2/NoRsp -> validate response -> copy out -> release buffer -> retry on -EAGAIN when path-based`.

Response validation and safety:
- `validate_t2()` checks Trans2 word count, parameter/data offsets, ByteCount, and negotiated buffer bounds before response decoding.
- `validate_ntransact()` bounds-checks NT Transact parameter/data regions against the SMB ByteCount area.
- Read paths check returned data length against `CIFSMaxBufSize` and requested count.
- Reparse point parsing validates data offsets, setup count, returned data length, reparse buffer length, and returns the response buffer to the caller on success.
- EA listing walks `fealist` entries with explicit list-length and end-of-SMB checks before copying names or values.

Notable data handling:
- Pathnames are encoded as UTF-16 when `SMBFLG2_UNICODE` is set; otherwise `copy_path_name()`/ASCII paths are used. Most conversions cap at `PATH_MAX` and use `cifs_remap()`.
- File IDs remain little-endian on the wire (`netfid`/`Fid` comments call this out repeatedly).
- Large-file capability changes read/write word counts and high-offset fields.
- Legacy paths support old servers via `SMBQueryInformation()`, `SMBOldQFSInfo()`, and `SMBSetInformation()`.
- Unix extension paths map Unix basic info, symlink/hardlink, POSIX create, POSIX locks, POSIX filesystem info, Unix caps, and POSIX ACL wire formats.

NetFS/async behavior:
- `cifs_async_readv()` and `cifs_async_writev()` submit async SMB1 read/write requests.
- `cifs_readv_callback()` verifies signatures when needed, accounts bytes, sets NetFS progress/EOF/retry flags, releases credits, terminates the read subrequest, and releases the MID.
- `cifs_writev_callback()` validates the response, masks bad OS/2 `CountHigh` values, maps short writes to `-ENOSPC`, sets progress, terminates the write subrequest, and restores credits.

Resource and retry notes:
- Path-based operations commonly retry internally on `-EAGAIN`; handle-based operations generally return to the caller because a reconnect invalidates the FID.
- Close/find-close/tree-disconnect/logoff suppress some reconnect errors because the server-side object is already gone after a dead session.
- Buffer ownership varies: most functions release their SMB buffer before return; search operations deliberately retain the response buffer in `cifs_search_info`; reparse query returns the response buffer to the caller.
- Care point: a few post-allocation `tcon->ses->server == NULL` checks in read/write paths return without local release in this file; callers and future edits should audit those lifetimes before refactoring.

Open issues embedded in comments:
- Lock reclaim after reconnect is still questioned.
- Several `BB/FIXME` notes ask for tighter max data sizing from session state, stronger buffer-overrun checks, better Trans2 EA validation, fallback logic for unsupported Unix search levels, and ACL overflow checks.
- Some legacy open response fields and timestamp conversions are intentionally incomplete or approximate.
