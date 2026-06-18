## sources/user-network-fs/go-fuse/fuse/constants_freebsd.go

Purpose: FreeBSD-specific definitions for syscall open flag constants that are not directly shared with Linux.

Important APIs/types/functions: defines `syscall_O_LARGEFILE` and `syscall_O_NOATIME` as FreeBSD-compatible bit values.

Control flow: compile-time constant selection through build constraints.

State and persistence: none.

Dependencies and integration: used by flag formatting and open request handling code that wants consistent symbolic support across OSes.

Risks and test signals: wrong values can misreport or mishandle open flags on FreeBSD. Coverage depends on FreeBSD builds/tests.
