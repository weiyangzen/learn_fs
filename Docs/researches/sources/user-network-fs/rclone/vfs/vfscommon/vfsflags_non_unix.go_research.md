# sources/user-network-fs/rclone/vfs/vfscommon/vfsflags_non_unix.go

## Purpose
Supplies default umask, uid, and gid values for platforms outside Linux, Darwin, and FreeBSD.

## APIs, Flow, And State
`getUmask` returns `0000`. `getUID` and `getGID` return all-ones `uint32`, which signals WinFSP-FUSE-style code to use the current user. There is no runtime state.

## Dependencies And Integration
Selected by build tags `!linux && !darwin && !freebsd` and used as defaults in `OptionsInfo`.

## Risks And Test Signals
The sentinel UID/GID semantics are platform-specific. Incorrect defaults can surface as odd ownership on mounted files. Coverage is mostly build-tag compilation and platform-specific mount testing.
