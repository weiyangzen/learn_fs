# sources/user-network-fs/go-fuse/fs/loopback_linux.go

Purpose: Linux-specific loopback helpers.

Important APIs: `unix_UTIME_OMIT` alias; `doCopyFileRange` uses `unix.CopyFileRange`; `intDev` returns int; `LoopbackNode.Statx` dispatches to file-handle `FileStatxer` when present, otherwise calls `unix.Statx` on the backing path and fills `fuse.StatxOut`.

Control flow/state: no independent state; operates on backing filesystem path or file handle.

Dependencies/integration: used by `LoopbackNode.CopyFileRange`, `Setattr`, and bridge statx. Risks include path-based statx following semantics controlled by flags, copy_file_range partial-copy behavior, and kernel capability differences. Linux tests cover copy file range and statx paths elsewhere in the suite.
