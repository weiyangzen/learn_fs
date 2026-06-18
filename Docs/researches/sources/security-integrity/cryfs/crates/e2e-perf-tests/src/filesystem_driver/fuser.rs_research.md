# sources/security-integrity/cryfs/crates/e2e-perf-tests/src/filesystem_driver/fuser.rs

## Purpose
Implements `FilesystemDriver` over rustfs's low-level FUSE-like API with configurable inode-cache modeling.

## Important APIs, types, and functions
- `FuserCacheBehavior` abstracts cached and uncached node handle behavior.
- `WithInodeCache` uses `InodeGuard`; `WithoutInodeCache` uses `AbsolutePathBuf` and explicit lookup/forget traversal.
- `_split_common` optimizes two-path lookup for rename.
- `InodeGuard` calls `forget` on drop.
- `FuserFilesystemDriver<C>` implements the full driver trait using `ObjectBasedFsAdapterLL`.
- `ReplyDirectoryImpl` and `ReadCallbackImpl` adapt callback-based APIs.

## Control flow
Driver methods load required inode(s) through the cache behavior, invoke low-level rustfs operations, and then either preserve inode guards or forget temporary inodes. Mutating metadata operations use `setattr` with only relevant fields set. Rename loads old/new parents together so common ancestors are not duplicated and same-directory moves use correct inode identity.

## State and persistence behavior
The driver owns an `AsyncDropArc<ObjectBasedFsAdapterLL<Device>>`. `WithInodeCache` holds inode references until handles drop; `WithoutInodeCache` forgets looked-up inodes after each operation to simulate cold kernel cache. Reset methods flush/reset filesystem caches. Underlying filesystem content persists in fixture stores.

## Dependencies and integration points
Bridges CryFS fixture devices to low-level rustfs APIs, FUSE root inode semantics, callback traits, and async drop. Operation modules use it to distinguish cached and uncached fuser performance.

## Risks and edge cases
Drop for `InodeGuardInner` blocks inside Tokio to call async forget/drop, which can deadlock if runtime assumptions change. Missing forget calls would skew operation counts and leak filesystem references. Callback capture unwraps assume APIs always call callbacks.

## Test signals
Operation-count tests instantiate fuser-with-cache and fuser-without-cache variants; expected counts in operation modules validate lookup/cache behavior.
