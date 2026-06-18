# File Research: sources/os/bsd/freebsd-src/sbin/fsck_msdosfs/dosfs.h

## Purpose

Defines FAT filesystem constants and architecture-independent in-memory data structures used by `fsck_msdosfs`.

## Key Definitions

- Boot sector sizes:
  - `DOSBOOTBLOCKSIZE_REAL` = 512
  - `DOSBOOTBLOCKSIZE` = 4096 for 4Kn reads
- Cluster type:
  - `typedef u_int32_t cl_t`
- `struct bootblock`:
  - Raw BPB fields
  - FAT32 extended fields
  - Derived layout fields
  - Filesystem statistics
- Cluster constants:
  - `CLUST_FREE`, `CLUST_FIRST`, `CLUST_RSRVD`, `CLUST_BAD`, `CLUST_EOFS`, `CLUST_EOF`, `CLUST_DEAD`
- FAT masks:
  - `CLUST12_MASK`, `CLUST16_MASK`, `CLUST32_MASK`
- Directory structures:
  - `struct dosDirEntry`
  - `struct dirTodoNode`
- Directory scan flags:
  - `DIREMPTY`, `DIREMPWARN`

## Integration Notes

Included by `ext.h`, which exposes the checker API. It is the shared type contract between boot parsing, FAT scanning, directory traversal, and check orchestration.
