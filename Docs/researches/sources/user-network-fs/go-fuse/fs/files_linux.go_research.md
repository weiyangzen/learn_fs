# sources/user-network-fs/go-fuse/fs/files_linux.go

Purpose: Linux-specific block defaulting and file-handle statx support.

Important functions: `setBlocks` and `setStatxBlocks` fill `Blksize=4096` and `Blocks=ceil(Size/4096)*8` when unset; `LoopbackFile.Statx` calls `unix.Statx` on the fd and fills `fuse.StatxOut`.

State/dependencies: reads size fields from attr/statx output; uses the loopback fd under mutex.

Integration/risks: used by bridge attr/statx normalization and loopback statx dispatch. Risks include assumptions about 4KiB block size and statx on fd with empty path/flags semantics. Linux statx and attr tests are relevant signals.
