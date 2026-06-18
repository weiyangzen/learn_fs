# File Research: sources/os/linux/linux-stable/fs/jffs2/gc.c

## Role

Implements JFFS2 garbage collection. It selects eraseblocks, verifies unchecked inodes before GC, moves live nodes out of dirty blocks, preserves required deletion markers, rewrites data/metadata/dirent nodes, handles pristine copies, and triggers block erasure when a GC block becomes fully obsolete.

## GC Block Selection

`jffs2_find_gc_block()` chooses a block from lists with probabilistic weighting:

- `bad_used_list` if enough free blocks exist;
- `erasable_list`;
- `very_dirty_list`;
- `dirty_list`;
- `clean_list`;
- fallback dirty/very-dirty/erasable lists;
- flushes writebuffer if only `erasable_pending_wbuf_list` can progress.

It sets `c->gcblock`, initializes `gc_node`, and converts any `wasted_size` in a selected clean block into dirty accounting.

## Main Pass

`jffs2_garbage_collect_pass()` performs one unit of progress:

- Takes `alloc_sem`.
- If unchecked space remains, scans inode caches and invokes `jffs2_do_crccheck_inode()` before real GC.
- Processes pending erases when available.
- Selects or reuses `c->gcblock`.
- Skips obsolete refs and dispatches live node handling.
- Handles inode-less nodes by copying pristine unknown compatible nodes or marking non-pristine ones obsolete.
- Handles xattr raw nodes through xattr GC hooks when enabled.
- Coordinates inode-cache states so absent pristine nodes can be copied without instantiating VFS inodes, while non-pristine or in-core nodes go through normal inode fetch.
- Moves fully obsoleted GC blocks to `erase_pending_list`.

## Live Node Handling

`jffs2_garbage_collect_live()` locks the inode-private `f->sem`, verifies the raw node is still live in the selected GC block, then classifies it as:

- metadata dnode;
- data dnode via fragment tree lookup;
- live dirent;
- deletion dirent;
- unexpected raw node, which triggers debug dump/BUG if not obsolete.

## Pristine Copy Path

`jffs2_garbage_collect_pristine()` copies a `REF_PRISTINE` node intact when it fits:

- reserves GC space;
- reads the full raw node;
- validates common header CRC;
- validates inode node/data CRC or dirent node/name CRC for known node types;
- copies the bytes to a new physical location;
- links a new pristine node ref;
- marks the old raw ref obsolete.
- Returns `-EBADFD` when the node cannot be copied intact and should be handled by slower rewriting.

## Rewrite Paths

- `jffs2_garbage_collect_metadata()` rewrites metadata-only inode nodes, including symlink target or device metadata, and replaces `f->metadata`.
- `jffs2_garbage_collect_dirent()` writes a replacement dirent with a new version and adds it back to the directory list.
- `jffs2_garbage_collect_deletion_dirent()` drops obsolete deletion dirents when safe; on media that cannot mark obsolete nodes permanently, it scans old obsolete dirents to decide whether the deletion marker must be preserved.
- `jffs2_garbage_collect_hole()` writes replacement zero-compressed hole nodes, preserving version for partially overlapped hole nodes when required.
- `jffs2_garbage_collect_dnode()` reads the relevant page through page cache, optionally expands the rewrite range to merge adjacent dirty fragments, compresses data through `jffs2_compress()`, writes new dnodes, and updates the fragment tree.

## Concurrency Notes

- `alloc_sem` serializes allocation and GC.
- `erase_completion_lock` protects block/list/ref state.
- `inocache_lock` protects inode cache state transitions.
- `f->sem` protects per-inode metadata, dents, and fragment trees.
- The data-node GC path drops `f->sem` before acquiring folio locks to obey lock ordering.

## Research Notes

This is the core maintenance engine for the log-structured filesystem. Its behavior depends heavily on raw node ref state: pristine nodes can often be copied byte-for-byte, while normal/overlapped nodes must be reconstructed from inode state and page-cache data.
