# sources/user-network-fs/go-fuse/fs/files_freebsd.go

Purpose: FreeBSD-specific no-op block defaulting helper.

Important API: `setBlocks(out *fuse.Attr)` intentionally does nothing.

Control flow/state: none.

Dependencies/integration: selected in FreeBSD builds and used by bridge attr normalization. Risks are minimal, but leaving block fields unset may affect callers that expect Linux-like `Blocks`/`Blksize`. Cross-build in `all.bash` is the primary signal.
