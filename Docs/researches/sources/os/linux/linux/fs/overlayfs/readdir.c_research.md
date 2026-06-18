# File Research: sources/os/linux/linux/fs/overlayfs/readdir.c

## Purpose

`readdir.c` implements overlayfs directory iteration, merged directory caching, whiteout filtering, xwhiteout handling, inode-number translation for directory entries, directory fsync/release/open operations, emptiness checks, and work/index directory cleanup.

## Main Responsibilities

- Read directory entries from real upper/lower directories under overlay credentials.
- Merge entries from multiple layers while hiding lower names shadowed by upper names.
- Filter whiteouts and xwhiteout entries from visible results.
- Maintain a per-directory cache for merged directory iteration.
- Translate `d_ino` values so readdir output stays consistent with overlay `stat(2)` behavior where possible.
- Handle casefolded comparison names when the overlay stack is casefolded.
- Support direct iteration of real directories when no merge cache is needed.
- Track and invalidate caches using overlay inode version counters.
- Check whether a merged directory is empty before removal.
- Clean up upper whiteouts, workdir leftovers, and stale/orphan index entries.

## Key Types

- `struct ovl_cache_entry`: one cached directory entry, with visible name, comparison name, real inode, translated inode, type, upper/whiteout/xwhiteout state, and RB-tree/list links.
- `struct ovl_dir_cache`: refcounted merged directory cache with version, list order, and name RB-tree.
- `struct ovl_readdir_data`: callback state used while reading real directories into caches.
- `struct ovl_dir_file`: per-open directory file state, including whether direct real iteration is possible, cached upperfile, realfile, and cursor.
- `struct ovl_readdir_translate`: state for translating real directory iteration into overlay-visible inode numbers.

## Important Functions

- `ovl_casefold()` creates normalized comparison names for casefolded layers.
- `ovl_cache_entry_find*()` manage RB-tree name lookup.
- `ovl_cache_entry_new()` allocates entries and marks candidates needing later inode or xwhiteout checks.
- `ovl_fill_merge()` adds entries during merged directory reads.
- `ovl_fill_lowest()` preserves reasonably stable offsets by inserting lowest-layer entries before upper ones.
- `ovl_check_whiteouts()` performs full lookup of character-device whiteout candidates.
- `ovl_dir_read()` opens and iterates one real directory.
- `ovl_dir_read_merged()` walks all real paths from `ovl_path_next()` and builds a merged cache.
- `ovl_cache_get()` obtains or rebuilds the merged cache if the inode version changed.
- `ovl_cache_update()` resolves delayed inode-number updates and xwhiteout checks.
- `ovl_dir_read_impure()` and `ovl_cache_get_impure()` build a special cache for impure real upper directories.
- `ovl_iterate_real()` directly iterates real dirs while translating `d_ino` when needed.
- `ovl_iterate_merged()` emits entries from the merged cache.
- `ovl_dir_open()`, `ovl_dir_llseek()`, `ovl_dir_fsync()`, and `ovl_dir_release()` implement directory file operations.
- `ovl_check_empty_dir()` verifies merged directory emptiness and collects upper whiteouts for cleanup.
- `ovl_cleanup_whiteouts()` removes selected upper whiteouts.
- `ovl_check_d_type_supported()` probes whether the upper/work filesystem supplies useful `d_type`.
- `ovl_workdir_cleanup()` recursively removes workdir leftovers.
- `ovl_indexdir_cleanup()` validates, removes, or whiteouts index entries during mount.

## Merge And Cache Flow

For merge directories, `ovl_iterate_merged()` obtains a cache via `ovl_cache_get()`. Cache construction reads each real directory in stack order. Upper and higher lower layers populate an RB-tree keyed by visible or casefolded name; lower duplicates are ignored. The lowest layer is inserted through a middle list so offsets are more stable across rebuilds.

Entries marked as whiteouts are skipped during emission. Character device whiteouts are checked after reading, while xwhiteout regular files are checked lazily with `ovl_cache_update()` because detecting them requires a real lookup and xattr check.

The cache is versioned with `ovl_inode_version_get()`. Directory mutations in `util.c` increment the version, causing existing open directory state to drop and rebuild stale caches.

## Inode Number Handling

The file tries to keep `readdir()` `d_ino` consistent with overlay `stat(2)`:

- Lower inode numbers can be remapped with xino bits and fsid.
- Upper entries in impure directories may need lookup/stat to match overlay inode identity.
- `.` and `..` can require recalculation.
- Origin-backed entries may require `vfs_getattr()` on the overlay path.
- If xino overflows, the real inode is used and a warning can be emitted for `xino=on`.

## Real Directory Fast Path

If a directory is real and does not require whiteout filtering or merge behavior, overlayfs can iterate the real file directly. It still may use `ovl_iterate_real()` for inode-number translation when xino is active, the parent is merged, or the directory is impure.

`ovl_dir_real_file()` handles directories that were opened as lower but later copied up, lazily opening and caching the upper real file.

## Workdir And Index Cleanup

`ovl_workdir_cleanup()` removes temporary workdir entries, recursing one level for directories. The special `work/incompat` path aborts mount with a clearer incompatibility error if non-empty.

`ovl_indexdir_cleanup()` scans the index directory at mount, verifies each index entry with `ovl_verify_index()`, removes stale entries, and whiteouts orphan index entries when NFS export needs stale file handles to remain blocked.

## Risk Notes

- Directory offsets are cache-derived for merged dirs and only best-effort stable.
- Casefolded comparison names must be used consistently or duplicate hiding can break.
- Whiteout and xwhiteout detection requires care because some checks are deferred until emission.
- Impure directory caches are not refcounted like merge caches and are rebuilt separately.
- Index cleanup is consistency-critical; aborting mount is preferred over continuing with incompatible index state.
