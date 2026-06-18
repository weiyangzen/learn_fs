# File Research: sources/os/linux/linux-stable/fs/omfs/dir.c

## Scope

This file implements OMFS directory hashing, lookup, create/mkdir, unlink/rmdir, rename, readdir, empty-directory initialization, and hash-chain validation.

## Main APIs

- `omfs_make_empty()` initializes an on-disk inode block either as a directory hash table or a regular-file extent table.
- `omfs_is_bad()` validates an inode/header self pointer and range.
- Directory inode ops: lookup, mkdir, create, unlink, rmdir, rename.
- Directory file ops: generic read, `iterate_shared` via `omfs_readdir()`, and generic llseek.

## Control Flow

- Directory entries are stored as hash buckets in the directory inode block. Each bucket points to a linked list of inode blocks through `i_sibling`.
- `omfs_hash()` lowercases bytes and XOR-shifts them into a bucket index.
- `omfs_find_entry()` reads the bucket head and follows the linked list with `omfs_scan_list()`.
- `omfs_add_link()` prepends a new inode into the proper bucket, stores its name, sibling, and parent pointers, and marks parent/child dirty for checksum rebuild.
- `omfs_delete_entry()` removes a target from either the bucket head or a previous inode’s sibling link.
- `omfs_remove()` rejects non-empty directories, unlinks the entry, clears link count, and marks metadata dirty.
- `omfs_rename()` supports only `RENAME_NOREPLACE`; it removes an existing target if present, deletes the old link, then adds the old inode under the new name.
- `omfs_readdir()` encodes bucket index and chain index in `ctx->pos`, emits dot entries first, then walks each bucket chain.

## Risks And Invariants

- `omfs_dir_is_empty()` appears semantically inverted: it returns `*ptr != ~0` after the loop, so callers use `!omfs_dir_is_empty()` to reject directories. The naming is misleading and fragile.
- Lookup compares `strncmp(oi->i_name, name, namelen)` without separately requiring a NUL or exact stored-name length match; names sharing the queried prefix can match.
- Hash-chain loops are not bounded except by corrupt self/range detection.
- Rename is not transactional; failures after deleting the old entry can leave namespace changes partially applied.
