# File Research: sources/os/linux/linux/fs/verity/Kconfig

## Purpose
Defines configuration options for fs-verity and optional builtin signature verification.

## Main Contents
- `config FS_VERITY`: bool option for read-only file-based authenticity protection.
  - Depends on `PAGE_SHIFT <= 16`.
  - Selects hash info and SHA-256/SHA-512 library support.
  - Help explains Merkle-tree verification for supported filesystems.
- `config FS_VERITY_BUILTIN_SIGNATURES`: optional builtin signature support.
  - Depends on `FS_VERITY`.
  - Selects `SYSTEM_DATA_VERIFICATION`.
  - Help warns that builtin signatures are not the only or always best signature mechanism.

## Cross-File Relationships
- Controls objects in `fs/verity/Makefile`.
- Supported filesystems call fs-verity helpers through `struct fsverity_operations`.

## Risks / Review Notes
- `PAGE_SHIFT <= 16` is tied to the pagecache Merkle-tree caching layout.
- Builtin signature support adds policy-sensitive keyring and PKCS#7 verification paths.
