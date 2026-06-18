# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fs/pc_node.h

This header defines PCFS in-core file/directory node structures and node operation declarations.

FID:
- `pc_fid` overlays VFS fid with length, directory-entry block, directory-entry offset, and creation-time generation approximation.

Node model:
- `pcnode` stores active-list links, flags, vnode, file size, starting cluster, directory-entry disk block/offset, cached directory entry, last visited cluster, and last cluster index.
- File nodes are identified by directory entry block/offset, while directory nodes use starting cluster.

Flags:
- Data modified, node changed, invalid, external vnode reference held, accessed, and release-hold states.

Conversions and node ids:
- `PCTOV` maps pcnode to vnode.
- `VTOPC` maps vnode to pcnode.
- `pc_makenodeid()` makes a pseudo inode: directories use negative cluster-based ids, files use directory-entry position.

Hashing:
- `NPCHASH` is currently 1, so file/directory hash macros collapse to one bucket.
- `pchead` stores linked-list heads.

Kernel API:
- Vnode ops for files and directories plus templates.
- Global file and directory head arrays.
- Node lifecycle, mark modified/accessed, sync/update, block mapping/allocation/free, filesystem verification/disk-change handling, directory lookup/enter/remove/rename, block-at-offset, truncate, file cluster sizing, page writeback, and bad filesystem marking.

Dependencies and relationships:
- Depends on `struct pcdir` from `pc_dir.h` and FAT/mount state from `pc_fs.h`.
- The cached directory entry is central to removable-media change detection.
