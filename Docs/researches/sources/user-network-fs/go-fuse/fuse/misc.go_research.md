## sources/user-network-fs/go-fuse/fuse/misc.go

Purpose: miscellaneous helpers for status conversion, owner discovery, and timestamp conversion.

Important APIs/types/functions: `Status.String`, `Status.Ok`, `ToStatus(error)`, `CurrentOwner`, and `UtimeToTimespec`. `ToStatus` maps nil to `OK`, syscall errors to negative statuses, and unknown errors to `EIO`.

Control flow: adapters call `ToStatus` around syscalls and Go file operations. `UtimeToTimespec` translates nil to platform `UTIME_OMIT`.

State and persistence: `CurrentOwner` reads process uid/gid; otherwise stateless.

Dependencies and integration: widely used by loopback, nodefs, pathfs, and raw server replies.

Risks and test signals: wrong error mapping changes kernel-visible errno. `misc_test.go` covers representative conversions.
