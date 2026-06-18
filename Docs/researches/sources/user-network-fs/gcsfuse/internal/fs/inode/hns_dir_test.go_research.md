# sources/user-network-fs/gcsfuse/internal/fs/inode/hns_dir_test.go

## Purpose

`hns_dir_test.go` validates `DirInode` behavior when hierarchical namespace support is enabled and compares it with non-HNS behavior for operations whose storage APIs differ. It focuses on HNS folder lookup, managed-folder style listing, folder rename/create/delete, file move, recursive deletion, and the type-cache-deprecation path that uses cache-only lookups before server fallback.

## Important APIs, Types, And Helpers

`hnsDirTest` holds shared context, `gcsx.SyncerBucket`, locked `DirInode`, testify mock bucket, optional `metadata.TypeCache`, clock, config, and parent inode context. `HNSDirTest` configures a hierarchical bucket; `NonHNSDirTest` configures a non-hierarchical bucket. `resetDirInodeWithTypeCacheConfigs` creates a `NewDirInode` with `EnableHns`, `EnableUnsupportedPathSupport`, managed-folder listing, and metadata cache settings. `createDirInodeWithTypeCacheDeprecationFlag` creates child dir inodes under a parent context.

The suite exercises `findExplicitFolder`, `LookUpChild`, `RenameFolder`, `RenameFile`, `DeleteChildDir`, `CreateChildDir`, `DeleteObjects`, `ReadEntries`, and cache-deprecated lookup paths.

## Control Flow And State Behavior

HNS lookup tests validate that explicit folders are found through `GetFolder`, not only directory marker objects. A not-found folder returns nil without error. For cached regular-file or symlink types, lookup goes through object stat; for explicit dir/unknown type, it can query `GetFolder`; cached nonexistent type suppresses remote lookup. Conflict marker names still allow object-side lookup when a folder also exists.

Rename tests validate HNS-specific `RenameFolder` and `MoveObject` requests, including propagation of `NotFoundError`. Create/delete tests split HNS and non-HNS behavior: HNS directory creation calls `CreateFolder`, while non-HNS creation creates an empty trailing-slash object with generation precondition. HNS deletion can need both object deletion and folder deletion; if folder deletion succeeds after object deletion fails, the directory inode is marked unlinked. If folder deletion fails, the error is surfaced and unlink state is retained false.

Recursive deletion tests verify deleting object names, descending through listed collapsed runs, and issuing both `DeleteObject` and `DeleteFolder` for HNS folders. HNS `ReadEntries` uses `IncludeFoldersAsPrefixes` and treats collapsed folder prefixes, explicit folder objects, and files as visible directory entries, with HNS implicit directories becoming explicit folder-type entries in the cache.

## Dependencies And Integration Points

The suite depends on `storagemock.TestifyMockBucket`, `gcsx.SyncerBucket`, GCS HNS folder APIs (`GetFolder`, `CreateFolder`, `DeleteFolder`, `RenameFolder`), object APIs (`StatObject`, `MoveObject`, `ListObjects`, `DeleteObject`), `metadata.TypeCache`, cache miss errors, FUSE dirents, config flags, and semaphores. It is the key test signal for integration between inode directory logic and HNS bucket semantics.

## Risks And Test Signals

Covered risks include using object APIs when HNS folder APIs are required, failing to update or bypass type cache correctly, wrong precedence between files and folders, recursive delete missing nested collapsed runs, and incorrect error handling when one of object/folder deletion succeeds. Type-cache-deprecated cache-hit/miss tests confirm cache-only requests are attempted first and server lookups happen only on cache miss. Remaining risks include real HNS pagination, managed folders in fake storage, and concurrent rename/delete interactions.
