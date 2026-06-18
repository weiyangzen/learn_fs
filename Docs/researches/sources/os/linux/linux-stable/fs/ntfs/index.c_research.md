# File Research: sources/os/linux/linux-stable/fs/ntfs/index.c

## Scope

This file implements NTFS index B+tree mechanics: index context lifetime, entry validation, lookup, insertion, deletion, split/reparent operations, index allocation block I/O, index bitmap management, directory filename insertion/removal, and ordered traversal.

## APIs And Control Flow

- `ntfs_index_entry_inconsistent()` validates entry key/data boundaries and, with a context, validates that entries sit inside the active index root/block.
- `ntfs_index_entry_mark_dirty()` marks either the resident `$INDEX_ROOT` MFT record dirty or defers current index block writeback through `ib_dirty`.
- Context management:
  - `ntfs_index_ctx_get()` allocates a context for a base inode/index name.
  - `ntfs_index_ctx_put()` releases attribute search contexts, writes dirty index blocks, frees block buffers, and drops index allocation inodes.
  - `ntfs_index_ctx_reinit()` resets a context after structural mutation while preserving target inode/name.
- Index block I/O uses `ntfs_inode_attr_pread()`/`pwrite()` against `$INDEX_ALLOCATION`, with MST pre-write/post-read fixups and `INDX`/VCN/size/header consistency checks.
- Entry helpers compute first/next/last/previous entries, duplicate entries with or without child VCNs, insert/delete by memmove, and set/get child VCNs.
- `ntfs_index_lookup()` searches `$INDEX_ROOT`, follows child VCNs through `$INDEX_ALLOCATION`, tracks parent VCNs and positions, and returns either a found entry or the insertion position for `-ENOENT`.
- Index bitmap helpers create `$BITMAP`, set/clear allocation bits, and find a free index block VCN.
- `ntfs_ir_reparent()` converts a small resident index root into a large index by moving existing entries into a newly allocated index block, leaving a root node pointer, and adding `$INDEX_ALLOCATION`/`$BITMAP` as needed.
- `ntfs_ie_add()` inserts an index entry. If the target root/block lacks space, it grows the root, reparents to allocation, or splits index blocks until insertion succeeds.
- `ntfs_index_add_filename()` builds a filename index entry and inserts it into a directory `$I30`.
- Deletion helpers handle leaf removal, internal-node successor replacement, empty-block removal, parent END-entry reparenting, root leafification, and bitmap bit clearing.
- `ntfs_index_remove()` repeatedly looks up and removes a key until structural retries are complete.
- `ntfs_index_walk_down()` and `ntfs_index_next()` implement ordered traversal for readdir and other index scans.

## State And Dependencies

Important state includes `struct ntfs_index_context`, `$INDEX_ROOT`, `$INDEX_ALLOCATION`, `$BITMAP`, parent VCN/position stacks, index block size/vcn sizing, collation rule, dirty index block state, and the base index inode.

This file depends on collation helpers, NTFS attribute lookup/add/truncate/record movement, attribute-list updates, fake attribute inode I/O, MFT dirty marking, and MST fixup helpers.

## Risks And Invariants

- Parent stack depth is capped by `MAX_PARENT_VCN`; overly deep indexes are rejected.
- Root growth can fail with `-ENOSPC`; the code may add an attribute list and move records away before retrying.
- Splitting uses median promotion, new bitmap allocation, tail copying, parent insertion, and source tail cutting. Rollback clears newly allocated bitmap bits on failure.
- Deletion from internal nodes replaces the removed entry with the leftmost successor from the right subtree; if replacement grows the containing node it may force split and retry.
- Index block writes apply MST fixups before write; sync write failure restores fixups through `post_write_mst_fixup()`.
- Several functions return `-EAGAIN` as an internal structural retry signal, not a final VFS error.
- The code assumes index root is resident and index allocation is non-resident; violations are corruption.
