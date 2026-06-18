# File Research: sources/os/linux/linux-stable/fs/jffs2/write.c

This file writes JFFS2 raw inode and dirent nodes and implements core create, unlink, and link mutations.

Key responsibilities:
- `jffs2_do_new_inode()` allocates and initializes a new inode cache, assigns an inode number, seeds raw inode header fields, and starts versioning at 1.
- `jffs2_write_dnode()` writes raw inode nodes plus optional data through kvecs, retries failed writes by reserving new space when allowed, marks partially written failed space obsolete, links successful raw refs, and classifies refs as pristine or normal.
- `jffs2_write_dirent()` writes raw dirent nodes plus names, validates names contain no embedded NULs, retries failed writes, links raw refs with dirent state, and returns full dirents.
- `jffs2_write_inode_range()` chunks a logical write by page boundary and available allocation, compresses data, fills all raw inode CRC/size/version fields, writes dnodes, inserts them into the fragment tree, and obsoletes stale metadata nodes.
- `jffs2_do_create()` writes the initial metadata inode node, initializes security labels and ACLs, writes the parent dirent, and links the dirent into the parent list.
- `jffs2_do_unlink()` either writes a deletion dirent when physical obsolete marking is unavailable or marks the existing dirent raw node obsolete in-place when possible; it also updates/deletes child inode link state and directory deletion dirents.
- `jffs2_do_link()` writes and files a new parent dirent for hard-link/rename-style operations.

Important interactions:
- Depends on reservation and completion paths in `nodemgmt.c`, compression helpers, CRC32, fragment-tree insertion, xattr/security/ACL initialization, and write-buffer/direct flash I/O.
- Uses `f->sem` or parent `dir_f->sem` to serialize per-inode metadata/list changes.

Notable invariants and risks:
- Raw node `hdr_crc`, `node_crc`, `data_crc`, size fields, offsets, versions, and endian conversion must be set before writing.
- If a write retry happens after another version has advanced, the node version is bumped and node CRC recomputed.
- Create is not atomic across inode-node, xattr/ACL initialization, and parent-dirent write; failures after the inode node can leave cleanup to later unlink/GC paths.
- Deletion behavior differs significantly between media that can physically clear `JFFS2_NODE_ACCURATE` and media that cannot.
