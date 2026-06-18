# File Research: sources/os/bsd/netbsd-src/sys/fs/adosfs/advnops.c

## Summary
Implements ADOSFS vnode operations for a read-only AmigaDOS filesystem.

## Main Responsibilities
- Define vnode operation table with unsupported mutating operations mapped to read-only or not-supported helpers.
- Report attributes from `anode` metadata, including timestamp conversion, uid/gid, permissions, size, and block usage.
- Read regular files via UBC for FFS variant or explicit block reads for OFS variant.
- Validate OFS data blocks by type and checksum.
- Map logical file blocks through AmigaDOS file-list block chains.
- Enumerate directories by walking per-directory hash chains and producing `dirent` records.
- Check read/execute permissions through kauth/genfs helpers and deny writes to regular files, directories, and symlinks.
- Return symlink targets from `ap->slinkto`.
- Recycle inactive vnodes and free anode tables/symlink buffers on reclaim.
- Provide pathconf values.

## Key Interfaces
- `adosfs_getattr()`, `adosfs_read()`, `adosfs_bmap()`, `adosfs_strategy()`, `adosfs_readdir()`, `adosfs_access()`, `adosfs_readlink()`, `adosfs_reclaim()`.

## Risks
`adosfs_bmap()` depends on valid file-list chains and caches the last indirect block in the anode. Directory offsets are synthetic slot counts based on `sizeof(struct dirent)`, not byte offsets in on-disk directories. Writes are universally unsupported.
