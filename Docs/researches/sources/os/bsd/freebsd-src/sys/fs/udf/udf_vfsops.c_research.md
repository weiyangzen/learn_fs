# File Research: sources/os/bsd/freebsd-src/sys/fs/udf/udf_vfsops.c

FreeBSD UDF VFS operations implementation for a read-only filesystem.

Key responsibilities:
- Registers UDF as `VFCF_READONLY` and module version 1.
- Creates and destroys UMA zones for translation buffers, UDF nodes, and directory stream objects.
- Implements mount option parsing, read-only enforcement, device lookup/access checks, GEOM open/close, optional kernel iconv setup, and mounted-from naming.
- Implements descriptor tag validation with checksum checking.
- Parses the UDF anchor at sector 256, scans the main volume descriptor sequence, records logical volume and partition information, validates the file set descriptor, and validates the root file entry.
- Implements unmount, root vnode retrieval, statfs, vnode construction through `udf_vget`, file-handle lookup, and partition map/sparing table parsing.

Dependencies:
- Uses FreeBSD VFS, vnode, namei, GEOM VFS, buffer cache, endian, UMA, and optional iconv APIs.
- Depends on `ecma167-udf.h`, `osta.h`, `udf.h`, and `udf_mount.h`.
- Relies on vnode operations from `udf_vnops.c`, including `udf_fifoops`.

Notable risks:
- Mount probing is narrow: it assumes 2048-byte logical sectors and checks anchor sector 256, with comments noting missing fallback anchor locations.
- The implementation supports limited partition map forms and effectively a single partition path.
- Some allocations use `M_NOWAIT`; mount can fail under memory pressure.
- `udf_vget` intentionally allows vnode creation races and resolves them through `vfs_hash_insert`, so cleanup and constructed-state ordering are sensitive.
- Sparing table validation calls `udf_checktag(..., 0)`, a compatibility-sensitive behavior for type 2 sparable maps.
