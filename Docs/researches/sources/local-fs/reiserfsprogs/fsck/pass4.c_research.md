# File Research: sources/local-fs/reiserfsprogs/fsck/pass4.c

`pass4.c` implements the final cleanup pass after semantic reachability has been computed.

Key responsibilities:
- Walks the tree starting from `root_dir_key`.
- Deletes every item whose item-header reachability flag remains unset.
- Clears residual item-header flags on retained items.
- Reports pass-4 statistics.
- Copies `fsck_new_bitmap(fs)` into the filesystem bitmap.
- Recomputes and stores the free-block count from the new bitmap.
- Flushes object-id map, bitmap, superblock, and all dirty buffers.

Important exported helper:
- `pass_4_check_unaccessed_items()`

Dependencies and data flow:
- Consumes reachability flags set by semantic rebuild/check logic.
- Consumes `fsck_new_bitmap(fs)` from rebuild passes.
- Calls `reiserfsck_delete_item()` for unreachable metadata and `id_map_flush()` before final flush.

Notable behavior:
- This pass is deliberately simple: semantic pass decides reachability; pass 4 removes everything not marked reachable.
- It also sanitizes retained item flags so repaired metadata does not keep fsck-only flags.
