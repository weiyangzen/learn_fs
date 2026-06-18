# File Research: sources/os/linux/linux/fs/f2fs/dir.c

## Summary
Implements F2FS directory lookup, filename preparation, dentry insertion/deletion, directory initialization, emptiness checks, and readdir. It supports encrypted filenames, casefolded Unicode lookup, inline dentries, hashed directory levels, and regular dentry blocks.

## Main Responsibilities
- Prepares `struct f2fs_filename` from VFS names using fscrypt and optional Unicode casefolding.
- Searches inline and regular directory entries by hash bucket or linear fallback.
- Adds, updates, and deletes directory entries.
- Initializes inode metadata and `.` / `..` entries for new directories.
- Maintains parent directory metadata, link counts, orphan handling, and directory depth.
- Emits directory entries for `iterate_shared`.
- Provides `f2fs_dir_operations`.

## Key APIs
- Filename setup: `f2fs_setup_filename()`, `f2fs_prepare_lookup()`, `f2fs_free_filename()`.
- Lookup: `f2fs_find_target_dentry()`, `f2fs_find_entry()`, `f2fs_parent_dir()`, `f2fs_inode_by_name()`.
- Mutation: `f2fs_add_dentry()`, `f2fs_do_add_link()`, `f2fs_delete_entry()`, `f2fs_set_link()`.
- Creation helpers: `f2fs_init_inode_metadata()`, `f2fs_do_make_empty_dir()`, `f2fs_do_tmpfile()`.
- Readdir: `f2fs_fill_dentries()`, `f2fs_dir_operations`.

## Important Behavior
Directory layout is hash-level based. `dir_buckets()`, `bucket_blocks()`, and `dir_block_index()` compute where a filename hash should be searched or inserted. `find_in_level()` searches the relevant bucket, records cached hash/level hints when room is found, and can fall back to linear search for casefold compatibility modes.

Filename setup wraps fscrypt preparation and computes the F2FS hash. For encrypted no-key names, the hash is decoded from the name. For casefolded directories, Unicode names may be casefolded into `cf_name`; strict encoding failures return `-EINVAL`, while non-strict failures fall back to opaque byte matching.

Insertion first tries inline dentries, then regular dentry blocks. `f2fs_add_regular_entry()` allocates dentry pages, finds free slots, initializes inode metadata if needed, writes the dentry, updates parent metadata, and manages directory depth.

Deletion clears the dentry bitmap slots, may truncate an emptied dentry block, updates parent timestamps, and drops the target inode link count. Directory emptiness ignores `.` and `..` in block zero and scans all other dentry bits.

`f2fs_fill_dentries()` validates name lengths, handles encrypted name conversion, emits entries with `dir_emit()`, optionally readaheads inode node pages, and marks the filesystem for fsck on corrupted zero-length or oversized dirents.

## State and Synchronization
Directory mutation uses folio locks, writeback waits, inode `i_sem` for inode metadata updates, `i_xattr_sem` for inline dentry insertion lock ordering, and F2FS operation locking supplied by callers where required. The directory inode caches a recent failed-lookup task and hash/level hint to speed create-after-lookup.

## Risks
Correctness depends on matching bitmap slot counts with encoded filename lengths. Casefold compatibility fallback can search without hashes, so callers must handle both hash and linear modes. Error handling during new inode metadata creation must clear link state and release orphan/tmpfile state correctly. Readdir corruption checks are defensive, but malformed on-disk dirents can still interrupt iteration with `-EFSCORRUPTED`.
