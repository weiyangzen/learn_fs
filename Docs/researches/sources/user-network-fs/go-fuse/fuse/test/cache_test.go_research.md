# `sources/user-network-fs/go-fuse/fuse/test/cache_test.go`

## Purpose
Integration tests for kernel data-cache control and nonseekable/read race behavior.

## Important APIs, Types, And Functions
Defines `cacheFs`, `setupCacheTest`, `TestFopenKeepCache`, `nonseekFs`, `TestNonseekable`, and `TestGetAttrRace`.

## Control Flow
Defines `cacheFs`, `setupCacheTest`, `TestFopenKeepCache`, `nonseekFs`, `TestNonseekable`, and `TestGetAttrRace`.

## State And Persistence
State uses temp backing/mount dirs and kernel cache TTLs. It validates `FOPEN_KEEP_CACHE`, explicit invalidation with `FileNotify`, nonseekable open flags, and concurrent create/stat behavior. Risks are kernel/version-dependent cache semantics and Darwin skip.

## Dependencies And Integration Points
Dependencies and integration are captured by the package imports and neighboring files in this subset.

## Risks And Edge Cases
State uses temp backing/mount dirs and kernel cache TTLs. It validates `FOPEN_KEEP_CACHE`, explicit invalidation with `FileNotify`, nonseekable open flags, and concurrent create/stat behavior. Risks are kernel/version-dependent cache semantics and Darwin skip.

## Test Signals
State uses temp backing/mount dirs and kernel cache TTLs. It validates `FOPEN_KEEP_CACHE`, explicit invalidation with `FileNotify`, nonseekable open flags, and concurrent create/stat behavior. Risks are kernel/version-dependent cache semantics and Darwin skip.
