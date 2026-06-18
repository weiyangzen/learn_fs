# sources/user-network-fs/go-fuse/fs/files_unix.go

Purpose: non-Darwin Unix timestamp update helper for `LoopbackFile`.

Important functions: `LoopbackFile.utimens` builds two `syscall.Timespec` values with `fuse.UtimeToTimespec`; `futimens` invokes `SYS_UTIMENSAT` with fd, null pathname, and flags zero to emulate `futimens(3)`.

State/dependencies: operates on the file descriptor in `LoopbackFile`.

Integration/risks: build-tagged `!darwin`, so it covers Linux and FreeBSD unless overridden. Risks include syscall availability and `unsafe.Pointer` usage. Timestamp behavior is indirectly tested by loopback setattr paths.
