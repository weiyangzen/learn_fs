# File Research: sources/os/linux/linux/fs/ext4/xattr.c

## Purpose
Implements ext4 extended attribute storage, lookup, listing, mutation, sharing, checksum validation, large-value EA inodes, inode-expansion migration, and cleanup. It is the core backend used by ext4 namespace handlers in `xattr_user.c`, `xattr_trusted.c`, `xattr_security.c`, and `xattr_hurd.c`.

## Main Responsibilities
- Supports both in-inode xattrs and external xattr blocks referenced by `EXT4_I(inode)->i_file_acl`.
- Shares identical external xattr blocks through `mb_cache` and reference counts.
- Supports large xattr values stored in separate EA inodes when `ea_inode` feature is enabled.
- Validates on-disk xattr structure, value offsets, checksums, ea-inode references, and size limits before use.
- Provides public operations: `ext4_xattr_get`, `ext4_listxattr`, `ext4_xattr_set`, `ext4_xattr_set_handle`, `ext4_xattr_delete_inode`, `ext4_expand_extra_isize_ea`, cache create/destroy helpers, and inode usage accounting.

## Key Data Flow
- Get path: `ext4_xattr_get()` takes `xattr_sem` read lock, searches inode body first via `ext4_xattr_ibody_get()`, then external block via `ext4_xattr_block_get()`.
- List path: `ext4_listxattr()` lists in-inode entries then block entries, filtering prefixes with namespace handlers and permissions.
- Set path: `ext4_xattr_set()` computes journal credits, starts a transaction, and delegates to `ext4_xattr_set_handle()`.
- Mutation path: `ext4_xattr_set_handle()` locks xattrs for write, finds existing inode/block entries, applies create/replace/remove semantics, chooses in-inode, xattr block, or EA inode storage, updates ctime/iversion, and marks fast commit ineligible.
- Delete path: `ext4_xattr_delete_inode()` decrements EA inode refs, releases xattr block refs, frees blocks, and clears `i_file_acl`.

## Important Implementation Details
- `check_xattrs()` is the core corruption gate. It validates xattr block headers, in-inode magic, entry list bounds, names without embedded NUL mismatch, EA inode feature constraints, value bounds, and overlap between name table and value area.
- Metadata checksums are handled by `ext4_xattr_block_csum()`, `ext4_xattr_block_csum_verify()`, and `ext4_xattr_block_csum_set()` when `metadata_csum` is enabled.
- `xattr_find_entry()` supports sorted external block lookup and unsorted in-inode lookup.
- `ext4_xattr_set_entry()` performs the packed entry/value layout edits, including inserting/removing names, moving value regions, zeroing padding, updating inline data offset, and recalculating entry/block hashes.
- `ext4_xattr_block_set()` handles copy-on-write for shared xattr blocks, mbcache reuse of identical blocks, quota charging, refcount saturation, allocation of new xattr blocks, and release of old blocks.
- EA inode support stores refcount in ctime/iversion and value hash in atime. It verifies stored value hashes and has compatibility handling for older Lustre-style EA inodes.
- `ext4_expand_extra_isize_ea()` makes room for larger inode extra fields by shifting in-inode xattrs or migrating selected xattrs to an external block.

## Concurrency and Journaling
- `EXT4_I(inode)->xattr_sem` protects `i_file_acl` and in-inode xattr state.
- External xattr blocks are only modified in place if exclusive; otherwise they are cloned.
- Buffer locks protect xattr block refcount/cache races.
- Journal credit estimation accounts for inode updates, xattr block ref/refree operations, quotas, inline-data expansion, EA inode allocation/data blocks, and old EA inode dereference.
- `ext4_journal_ensure_credits_fn()` is used during bulk EA inode ref decrements to safely survive transaction restarts.

## Edge Cases and Failure Modes
- Returns `-EFSCORRUPTED` or `-EFSBADCRC` for malformed or checksum-invalid metadata.
- Treats xattr names longer than 255 as `-ERANGE`.
- Avoids xattr recursion during write lock by overloading `EXT4_STATE_NO_EXPAND` through helpers in `xattr.h`.
- Refcount wraparound on EA inodes is detected and reported.
- Shared block refcount cannot exceed `EXT4_XATTR_REFCOUNT_MAX`; saturated blocks are marked non-reusable.
- Large values may retry storage as EA inodes if they do not fit in xattr block storage.
