# sources/user-network-fs/samba/source3/modules/vfs_fake_perms.c

## Purpose
`vfs_fake_perms.c` makes stat results appear owned by the current user/group and mode `0700`, without changing the filesystem.

## Important APIs, Types, And Functions
`fake_perms_stat()` wraps `SMB_VFS_NEXT_STAT()` and rewrites `smb_fname->st`. `fake_perms_fstat()` wraps `SMB_VFS_NEXT_FSTAT()` and rewrites the stat buffer. Both prefer `session_info->unix_token` and fall back to effective uid/gid for artificial connections.

## Control Flow
The hook delegates and exits on lower failure. Directories are reported as `S_IFDIR | S_IRWXU`; non-directories are reported as `S_IRWXU`. uid/gid are replaced with session or effective credentials.

## State And Persistence
There is no private or persistent state. Only returned stat data changes.

## Dependencies And Integration Points
The module depends on stat/fstat VFS hooks, connection session info, unix security tokens, and POSIX mode macros.

## Risks
Only stat and fstat are wrapped; lstat and fstatat may reveal real permissions. Non-directory type bits are discarded. Artificial connection fallback may not match SMB identity.

## Test Signals
Test file and directory overlays, session token uid/gid, artificial connection fallback, lower error propagation, and unwrapped lstat/fstatat contrast.
