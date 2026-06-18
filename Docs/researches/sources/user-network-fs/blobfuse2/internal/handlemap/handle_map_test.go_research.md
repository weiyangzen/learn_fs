<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/internal/handlemap/handle_map_test.go -->
# sources/user-network-fs/blobfuse2/internal/handlemap/handle_map_test.go

## Purpose
Unit test suite for the handle map package. It verifies handle construction, handle flag helpers, auxiliary value storage, cache object attachment, global handle registration, lookup, and deletion.

## Important APIs, Types, and Functions
`HandleMapSuite` is a `testify/suite` test fixture with an assertion helper. `TestNewHandle` validates `NewHandle` default state: `InvalidHandleID` and preserved path. `TestHandleFlags` exercises `Dirty`, `Fsynced`, `Cached`, `SetFileObject`, `GetFileObject`, `SetValue`, `GetValue`, `RemoveValue`, and `Cleanup`. `TestHandleMap` covers `GetHandles`, `Add`, `Load`, `Delete`, `CreateCacheObject`, and `Store`. `TestUnMountCommand` is the suite entry point despite the misleading name.

## Control Flow and State
Each test creates fresh handles but uses package-level handle-map state through `Add`, `Load`, and `Delete`. The suite checks that inserted handles receive nonzero IDs, can be loaded by ID, and disappear after deletion. Per-handle key/value state is populated and cleared via `Cleanup`; file object state is stored as an `*os.File` pointer.

## Dependencies and Integration Points
The tests depend on `github.com/stretchr/testify/assert` and `github.com/stretchr/testify/suite`. They integrate with the production `handlemap` package rather than mocks, so failures signal behavioral drift in the in-memory handle registry used by FUSE file operations.

## Risks and Edge Cases
The test assumes global handle-map state is clean enough between tests. It does not cover concurrent add/load/delete behavior, ID overflow, duplicate deletion, or cleanup interaction with real cache objects. The `TestUnMountCommand` name can mislead test selection and reporting.

## Test Signals
Passing tests show basic handle lifecycle and flag/value helpers work. Missing signals include race safety, cache object semantics beyond non-nil creation, and behavior under many handles.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/internal/handlemap/handle_map_test.go -->
