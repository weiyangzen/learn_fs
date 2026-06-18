## sources/user-network-fs/go-fuse/fuse/misc_unix.go

Purpose: Unix-specific `_UTIME_OMIT` value for timestamp syscalls.

Important APIs/types/functions: defines `_UTIME_OMIT = unix.UTIME_OMIT`.

Control flow: selected on platforms with `golang.org/x/sys/unix` support.

State and persistence: none.

Dependencies and integration: used by `UtimeToTimespec` and file timestamp update paths.

Risks and test signals: timestamp preservation during `utimens` and setattr depends on correct value.
