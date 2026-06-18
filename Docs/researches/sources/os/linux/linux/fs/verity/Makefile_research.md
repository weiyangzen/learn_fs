# File Research: sources/os/linux/linux/fs/verity/Makefile

## Purpose
Builds fs-verity implementation objects.

## Main Contents
- `CONFIG_FS_VERITY` builds `enable.o`, `hash_algs.o`, `init.o`, `measure.o`, `open.o`, `pagecache.o`, `read_metadata.o`, and `verify.o`.
- `CONFIG_FS_VERITY_BUILTIN_SIGNATURES` additionally builds `signature.o`.

## Cross-File Relationships
- Matches the subsystem split: enabling, hash algorithms, initialization, digest reporting, metadata loading, pagecache helpers, metadata ioctl, data verification, and optional signatures.

## Risks / Review Notes
- Signature support is intentionally optional and isolated in `signature.o`.
