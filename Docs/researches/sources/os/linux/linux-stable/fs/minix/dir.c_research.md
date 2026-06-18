# File Research: sources/os/linux/linux-stable/fs/minix/dir.c

## Summary
Minix directory read, lookup, insertion, deletion, emptiness, and dotdot helpers.

## Main APIs
`minix_readdir()`, `minix_find_entry()`, `minix_add_link()`, `minix_delete_entry()`, `minix_make_empty()`, `minix_empty_dir()`, `minix_set_link()`, `minix_dotdot()`, and `minix_inode_by_name()`.

## Behavior
Directory entries are fixed-size records from `sbi->s_dirsize`, with V1/V2 and V3 inode/name layouts handled separately. Readdir aligns `ctx->pos` to entry size, maps folios, skips zero-inode entries, and emits names with `DT_UNKNOWN`. Lookup scans mapped folios and returns a still-mapped entry. Add-link searches for a free or end-of-directory slot, prepares the folio chunk, writes the name/inode, extends size if needed, updates timestamps, and syncs directory metadata for dirsync.

## State and Synchronization
Directory modification locks the target folio and uses `minix_prepare_chunk()` plus `block_write_end()` through `dir_commit_chunk()`. Folios are kmap-local mapped and must be released by callers.

## Dependencies
Page cache folios, buffer-head write helpers, Minix directory sizing/name limits, `minix_fsync()`, and VFS dir iteration.

## Risks
Callers of `minix_find_entry()` and `minix_dotdot()` inherit responsibility for `folio_release_kmap()`. Version-specific entry layouts differ only by inode field width/offset, so casts must track `s_version`. Directory expansion writes outside current `i_size` under folio lock.
