# sources/user-network-fs/bazil-fuse/fuse_kernel.go

Purpose: `fuse_kernel.go` is the Go representation of the FUSE kernel wire protocol. It defines protocol version limits, opcode constants, bit flags, kernel input/output structs, and formatting helpers used by `fuse.go` to parse requests and serialize replies.

Important APIs, types, and functions: It exports flag types and constants such as `AttrFlags`, `GetattrFlags`, `SetattrValid`, `OpenFlags`, `OpenRequestFlags`, `OpenResponseFlags`, `InitFlags`, `ReleaseFlags`, `ReadFlags`, `WriteFlags`, `SetxattrFlags`, `LockFlags`, `LockType`, `PollFlags`, `PollEvents`, and `FAllocateFlags`. Helpers such as `entryOutSize`, `attrOutSize`, `mknodInSize`, `mkdirInSize`, `createInSize`, `readInSize`, `writeInSize`, and `setxattrInSize` encode protocol-version-specific struct sizing. Internal structs mirror kernel ABI messages.

Control flow: The file mostly contains declarations. The key dynamic behavior is flag formatting through `flagString` and version-gated size helpers. `OpenFlags` access-mode helpers mask with `OpenAccessModeMask` because read-only/write-only/read-write are alternatives rather than independent bits.

State and persistence behavior: There is no runtime state. The declarations define how transient kernel messages are interpreted by other files.

Dependencies and integration points: It uses `syscall`, `unsafe`, and `golang.org/x/sys/unix`. `fuse.go` relies on these definitions for every message parse and response. Platform-specific `openFlags` helpers in `fuse_kernel_linux.go` and `fuse_kernel_freebsd.go` adapt OS flag quirks before values become exported `OpenFlags`.

Risks: ABI drift is the main risk. Incorrect field order, padding, version-gated sizes, opcode values, or flag constants would corrupt protocol parsing. `unsafe.Sizeof` and `unsafe.Offsetof` require the Go structs to match C kernel layout. Comments note incomplete or platform-odd behavior around FreeBSD locks, FUSE submounts, setxattr extensions, and fallocate mode support.

Test signals: `fuse_kernel_test.go` validates open access mode masking and string formatting. `serve_test.go` indirectly exercises many struct definitions by driving real kernel operations.
