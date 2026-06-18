# sources/user-network-fs/bazil-fuse/fuse_kernel_freebsd.go

Purpose: This FreeBSD-specific adapter converts raw open flags from kernel messages into `OpenFlags`.

Important APIs, types, and functions: It defines `openFlags(flags uint32) OpenFlags`, returning `OpenFlags(flags)` unchanged.

Control flow: No branching; all flag bits are passed through.

State and persistence behavior: No state or persistence.

Dependencies and integration points: Called by `fuse.go` while decoding open, read, write, create, and release requests. It pairs with `fuse_kernel_linux.go`, which masks Linux-specific ABI noise.

Risks: Passing all bits through is correct only if FreeBSD FUSE uses the same meaningful flag surface expected by the package. Other tests note FreeBSD does not always pass append/truncate/lock fields the same way Linux does.

Test signals: `serve_test.go` contains FreeBSD-specific expectations for file flags, create flags, lock behavior, and open non-seekable behavior.
