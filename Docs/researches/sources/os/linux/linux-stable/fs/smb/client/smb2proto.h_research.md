# File Research: sources/os/linux/linux-stable/fs/smb/client/smb2proto.h

## Summary
Declares the internal SMB2/SMB3 client API used across the CIFS client. It exposes error mapping, message validation, signing/receive helpers, request setup, oplock and lease handling, path/reparse helpers, SMB2 worker functions, replay helpers, and protocol-specific metadata operations.

## Main Responsibilities
- Provide prototypes for SMB2 status-to-Linux-error mapping and optional KUnit-test access to the error map.
- Declare message size/data-area validation and UTF-16 path conversion helpers.
- Declare signing, receive checking, MID setup, async setup, tcon lookup, lease-state parsing, and oplock-break validation helpers.
- Expose path-info, reparse-point, symlink, mkdir/rmdir/unlink/rename/hardlink, and pending-delete helpers implemented outside `smb2pdu.c`.
- Declare all core SMB2 worker functions for negotiate, session setup, logoff, tcon/tdis, open, close, IOCTL, query, set, read/write, directory, locks, lease/oplock breaks, filesystem info, and validate-negotiate.
- Declare replay, compounding, preauth hash, encryption predicate, and response-buffer validation helpers.
- Expose SMB3 POSIX parsing helpers for directory and create-response consumers.

## Key Interfaces
Important public surfaces include `SMB2_negotiate()`, `SMB2_sess_setup()`, `SMB2_tcon()`, `SMB2_open()`, `SMB2_ioctl()`, `SMB2_query_info()`, `smb2_async_readv()`, `smb2_async_writev()`, `SMB2_query_directory()`, `SMB2_set_eof()`, `SMB2_lock()`, `SMB2_lease_break()`, `smb3_validate_negotiate()`, `smb2_verify_signature()`, `smb2_check_receive()`, `smb2_setup_request()`, `smb2_setup_async_request()`, and `smb2_reconnect_server()`.

## Important Behavior
This header is the cross-module contract for SMB2 dialect implementations. Many declarations have paired init/free forms so callers can build compound requests or reuse the same PDU construction helpers without sending immediately. It also separates protocol-neutral VFS operations from SMB2-specific implementation details, allowing dialect operation tables to point at these functions.

## Cross-File Interactions
Implemented functions are distributed across `smb2pdu.c`, `smb2transport.c`, `smb2misc.c`, `smb2ops.c`, `smb2maperror.c`, `smb2inode.c`, and adjacent CIFS client modules. Callers include connection setup, VFS file and directory operations, inode metadata paths, readdir, DFS/reparse handling, and netfs I/O.

## Risks
Prototype changes have broad blast radius because this is the primary SMB2 internal API. Init/free pair contracts and buffer ownership expectations are especially important; mismatches can leak CIFS buffers, free caller-owned response vectors, or break compound request construction.
