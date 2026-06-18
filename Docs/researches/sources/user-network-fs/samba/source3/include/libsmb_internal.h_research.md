# sources/user-network-fs/samba/source3/include/libsmb_internal.h

## Purpose
`libsmb_internal.h` is the private internal contract for `libsmbclient`. It defines internal server/file/context structures, DOS attribute descriptors, xattr mode constants, and prototypes for cache, directory, file, path, print job, server, stat, and xattr helpers.

## Important APIs, Types, And Functions
- `SMBC_MAX_NAME` bounds internal names.
- `struct DOS_ATTR_DESC` carries DOS attribute metadata including mode, size, times, and inode.
- `SMB_CTX_FLAG_USE_NT_HASH` extends public context flags.
- `SMBC_XATTR_MODE_*` constants describe internal xattr update operations.
- `struct _SMBCSRV` caches a server connection, device id, pathinfo capability flags, policy handle, echo time, and list links.
- `struct _SMBCFILE` tracks open files/directories, target cli, filename, offset, server, directory entry lists, errors, and list links.
- `struct SMBC_internal_data` stores initialization state, dirent buffer, cached servers, open files, time-name mode, POSIX extension preference, share mode, auth callback, user data, encryption level, case sensitivity, DFS credentials, server cache, POSIX emulation callbacks, high-level SMB callbacks, port, loadparm context, and memory context.
- Prototypes cover `SMBC_add/get/remove/purge_cached_server`, directory functions, file read/write/splice/close/attr functions, path parsing, print job helpers, server lookup/connect/cache cleanup, stat/statvfs helpers, and xattr operations.

## Control Flow
Public `libsmbclient` APIs operate on `SMBCCTX`, whose internal data points at these structures. Path parsing resolves workgroup/server/share/path/user/password/options, server lookup reuses or opens cached `SMBCSRV` connections, file/dir operations allocate `SMBCFILE`, and xattr/stat/print helpers dispatch to SMB protocol functions through cached `cli_state` connections.

## State And Persistence
The main state is process-local client library cache: server connections, open file/dir handles, directory listing buffers, authentication callbacks, DFS credentials, and loadparm context. Persistent effects occur through operations declared here: remote file changes, xattr updates, print jobs, and server/session cache reuse.

## Dependencies And Integration Points
It includes public `libsmbclient.h`, clirap helpers, source3 `includes.h`, `cli_state`, loadparm, POSIX emulation callbacks, and internal libsmb modules. It is private and should not be consumed by external applications.

## Risks
Internal structures are broad and shared across many modules, so field changes can ripple through the library. The fixed `_dirent_name` buffer must be large enough for URL-encoded names and comments. Server/file linked lists require consistent insertion/removal to avoid stale handles. DFS target connections mean `SMBCFILE.targetcli` can differ from `srv->cli`.

## Test Signals
Test server cache reuse/purge, open file and directory lifecycle, DFS referral target handling, auth callback selection, POSIX extension fallback, encryption level behavior, stat/xattr naming modes, print job helpers, and memory cleanup of linked lists.
