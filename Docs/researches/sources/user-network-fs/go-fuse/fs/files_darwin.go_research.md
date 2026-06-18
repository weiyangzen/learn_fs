# sources/user-network-fs/go-fuse/fs/files_darwin.go

Purpose: Darwin-specific file helpers for block defaults and timestamp updates.

Important functions: `setBlocks` is a no-op on Darwin; `LoopbackFile.utimens` emulates `utimensat`/`UTIME_OMIT` using `Futimes`, first calling `Getattr` when either atime or mtime should be preserved.

State/dependencies: uses the file descriptor in `LoopbackFile` and current attrs when preserving times.

Integration/risks: selected for Darwin builds. Risks include timestamp precision loss from timeval microseconds and extra getattr calls. Cross-builds provide compile signal; runtime timestamp behavior needs macOS coverage.
