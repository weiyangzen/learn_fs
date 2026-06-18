# sources/user-network-fs/go-fuse/fs/loopback_darwin.go

Purpose: Darwin-specific loopback helpers.

Important APIs: defines `unix_UTIME_OMIT` fallback, `timeToTimeval` conversion for pre-1970-safe timeval creation, `doCopyFileRange` returning `ENOSYS`, and `intDev` converting device numbers to int.

Control flow/state: no retained state; platform adapter only.

Dependencies/integration: selected on Darwin; used by loopback setattr and copy-file-range code paths. Risks include unavailable copy_file_range on Darwin and timestamp compatibility. Cross-build is the main CI signal; runtime coverage requires macOS FUSE tests.
