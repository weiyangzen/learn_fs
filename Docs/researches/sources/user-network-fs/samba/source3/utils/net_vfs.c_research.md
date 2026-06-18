# sources/user-network-fs/samba/source3/utils/net_vfs.c

## Purpose
Implements local `net vfs` operations that run through Samba VFS context: `getntacl` and `stream2adouble`.

## Important APIs, Types, and Functions
Global `struct net_vfs_state` stores context, session info, connection wrapper, and connection. `net_vfs_init()` loads Samba config/registry shares, initializes locking, creates system or user session info, resolves the share, creates a connection, and becomes that session user. `net_vfs_get_ntacl()` opens a path through VFS and calls `SMB_VFS_FGET_NT_ACL()`. `net_vfs_stream_to_appledouble()` calls `ad_unconvert()` directly or through `nftw()`.

## Control Flow
Both subcommands require a share and initialize the VFS context. `getntacl` converts and opens a path, retrieves owner/group/DACL security info, closes handles, and prints the descriptor. `stream2adouble` rejects absolute paths, then converts each path or recursively walks with symlink behavior controlled by options.

## State and Persistence
`getntacl` is read-only. `stream2adouble` may transform file stream/AppleDouble sidecar state through the VFS stack. The command also initializes locking and smbd-like connection state.

## Dependencies and Integration Points
Depends on loadparm, registry shares, auth/session setup, smbd connection helpers, filename conversion, VFS create/get-ACL calls, security descriptor printing, AppleDouble conversion, and global messaging.

## Risks
Requires root unless uid-wrapper is active. Recursive conversion can touch many files; symlink following changes risk. Static global state is not thread-safe. Correct behavior depends on full smbd/VFS initialization outside smbd.

## Test Signals
Cover privilege checks, unknown share, config/locking/session failures, ACL retrieval and close errors, absolute path rejection, recursive and non-recursive conversion, symlink skip/follow, `--continue`, verbose output, and conversion failures.
