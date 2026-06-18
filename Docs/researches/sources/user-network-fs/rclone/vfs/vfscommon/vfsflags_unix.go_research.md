# sources/user-network-fs/rclone/vfs/vfscommon/vfsflags_unix.go

## Purpose
Supplies Unix-family defaults for VFS umask, uid, and gid options.

## APIs, Flow, And State
`getUmask` temporarily sets umask to zero to read the current value, then restores it. `getUID` and `getGID` return effective user and group IDs. No state is retained, but `getUmask` briefly mutates process-global umask.

## Dependencies And Integration
Selected on Linux, Darwin, and FreeBSD. Uses `golang.org/x/sys/unix` and feeds defaults into `OptionsInfo`.

## Risks And Test Signals
Because umask is process-global, concurrent calls during startup would be sensitive, though option initialization is expected early. Tests indirectly validate permissions through `vfstest` directory/file/link mode checks.
