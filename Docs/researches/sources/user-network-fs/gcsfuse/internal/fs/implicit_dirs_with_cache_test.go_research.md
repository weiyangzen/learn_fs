<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/implicit_dirs_with_cache_test.go -->
# sources/user-network-fs/gcsfuse/internal/fs/implicit_dirs_with_cache_test.go

## Purpose

This small integration test suite validates recursive removal and rename of implicit directories when directory type caching is enabled.

## Important APIs, Types, and Functions

`ImplicitDirsWithCacheTest` embeds `fsTest`, enables implicit directories, and sets `DirTypeCacheTTL` to three minutes. `TestRemoveAll` invokes external `rm -r` on an implicit directory. `TestRenameImplicitDir` uses `os.Rename` and validates the moved descendants.

## Control Flow

Tests seed fake GCS objects under `foo/`, making `foo` an implicit directory. `TestRemoveAll` runs `rm -r <mount>/foo/` and expects no output or error. `TestRenameImplicitDir` renames `foo` to `fooNew`, stats the destination directory and children, and verifies the original path no longer exists.

## State and Persistence Behavior

State lives in the fake bucket, mounted filesystem, and type cache. The tests specifically exercise cache-aware operations that update or invalidate cached type knowledge during recursive remove or rename.

## Dependencies and Integration Points

The suite integrates `fsTest`, implicit directory lookup/listing, type cache TTL behavior, OS commands, POSIX rename, and recursive delete/rename logic in the filesystem layer.

## Risks and Edge Cases

External `rm` behavior depends on the host command. Rename and recursive delete of implicit directories require translating a synthetic directory into operations on descendant objects while maintaining cache correctness. The test verifies visible results but not the exact bucket object list after operations.

## Test Signals

Signals are successful `rm -r`, successful rename, destination stats for directory and child files, and source-path not-found error.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/implicit_dirs_with_cache_test.go -->
