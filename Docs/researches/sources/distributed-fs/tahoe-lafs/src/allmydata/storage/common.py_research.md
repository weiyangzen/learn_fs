# sources/distributed-fs/tahoe-lafs/src/allmydata/storage/common.py

## Purpose
Provides common storage helpers: storage-index base32 conversion, share directory layout, and unknown share container version exceptions.

## Important APIs, Types, and Functions
Defines `UnknownContainerVersionError`, `UnknownMutableContainerVersionError`, `UnknownImmutableContainerVersionError`, re-exports `DataTooLargeError`, and provides `si_b2a()`, `si_a2b()`, `si_to_human_readable()`, and `storage_index_to_dir()`.

## Control Flow
The conversion helpers are thin wrappers around Tahoe base32 utilities. `storage_index_to_dir()` encodes the storage index and returns `<first-two-chars>/<full-storage-index>` for share directory fanout.

## State and Persistence Behavior
No state. The directory-layout helper is central to persistent storage paths but does not itself touch disk.

## Dependencies and Integration Points
Used by storage server, crawler, HTTP client/server logging/path conversion, and tests. The exception types are raised by immutable/mutable share-file readers when on-disk magic/version values are unknown.

## Risks and Edge Cases
The functions assume valid storage-index bytes or base32 input; invalid values raise from lower-level base32 assertions/errors. Directory fanout is coupled to the on-disk share tree layout.

## Test Signals
`test_storage.py::UtilTests` covers encoding and `storage_index_to_dir()`, and corrupt-version tests exercise exception paths.
