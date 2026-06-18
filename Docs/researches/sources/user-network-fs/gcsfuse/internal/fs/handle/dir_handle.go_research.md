<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/handle/dir_handle.go -->
# sources/user-network-fs/gcsfuse/internal/fs/handle/dir_handle.go

## Purpose

This file implements `DirHandle`, the FUSE directory-handle state used to serve `ReadDir` and `ReadDirPlus` from a `inode.DirInode`. It buffers directory entries per handle, resolves GCS file-vs-directory name conflicts, merges unsynced local file entries, and assigns FUSE directory offsets.

## Important APIs, Types, and Functions

`DirEntry` abstracts common operations over `fuseutil.Dirent` and `fuseutil.DirentPlus`. The private wrappers `dirent` and `direntPlus` adapt the concrete FUSE types. `DirHandle` stores the backing `inode.DirInode`, an `implicitDirs` flag, a locker, cached `entries`, cached `entriesPlus`, and validity flags.

`NewDirHandle` constructs the handle and invariant-checking lock. `fixConflictingNames` expects sorted entries and appends `inode.ConflictingFileNameSuffix` to the non-directory side of a file/directory name conflict. It also suppresses duplicate file entries when the same file exists in both GCS and local pending entries. `sortAndResolveEntries` merges local entries, sorts, resolves conflicts, and assigns offsets. `readAllEntries` and `readAllEntryCores` page through inode listing APIs. Public methods are `ReadDir`, `FetchEntryCores`, and `ReadDirPlus`.

## Control Flow

`ReadDir` resets cached entries when offset is zero, lazily calls `ensureEntries`, validates the seek offset, then writes dirents into the caller buffer until full. `ensureEntries` locks the inode, reads all paginated entries, sorts and resolves names, then stores the cache. `FetchEntryCores` similarly resets plus-cache state on offset zero and reads all entry cores if the plus cache is invalid. `ReadDirPlus` consumes prebuilt `DirentPlus` entries, merges local entries, sorts/resolves/offsets them once, and writes `DirentPlus` responses from the requested offset.

## State and Persistence Behavior

State is per open directory handle. Cached entry slices persist until offset zero rewinds or the handle is discarded. Offsets are one-based and consecutive. Each listed entry receives a bogus non-root inode ID in `readAllEntries` because FUSE `readdir` does not produce lookup-count forgets for minted IDs. There is no disk persistence.

## Dependencies and Integration Points

The handle depends on `internal/fs/inode` for directory listing and conflict suffix semantics, `internal/locker` for invariant locks, FUSE ops/util types for ABI-facing dirent encoding, and Go `cmp`, `maps`, and `slices`. It sits between the filesystem operation handlers and `DirInode` implementations such as `dirInode` and `baseDirInode`.

## Risks and Edge Cases

Correctness depends on sorted input before conflict resolution, stable offset assignment, and duplicate handling for local-vs-GCS file entries. Invalid `seekdir` offsets return `fuse.EINVAL`. The fake inode ID strategy is a known tradeoff. `FetchEntryCores` returns nil cores when the plus cache is already valid and offset is nonzero, so callers must preserve previously fetched plus entries.

## Test Signals

The paired tests cover GCS-only, local-only, mixed local/GCS listings, duplicate same-name local/GCS files, local file vs GCS directory conflict suffixing, empty listings, `ReadEntryCores`, `FetchEntryCores` cache behavior, and `ReadDirPlus` conflict/offset behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/handle/dir_handle.go -->
