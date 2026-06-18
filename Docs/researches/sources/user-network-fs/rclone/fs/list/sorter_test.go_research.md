# sources/user-network-fs/rclone/fs/list/sorter_test.go

## Purpose
`sorter_test.go` tests the in-memory and external-sort behavior of `Sorter`, including custom keys, object/directory reconstruction, cutoff boundaries, temp-file errors, and benchmark-scale throughput.

## Important APIs, types, and functions
The suite targets `NewSorter`, `Sorter.Add`, `Sorter.Send`, `Sorter.CleanUp`, `SortToChan` indirectly, and custom `KeyFn` behavior. `testFs` and `benchFs` implement the minimal `NewObjecter` interface needed to rehydrate objects in external mode.

## Control flow
Tests add unsorted mock entries, assert unsorted internal state before `Send`, then require callback order. `testSorterExt` builds maps of mixed mock objects/directories, feeds them in arbitrary order, checks whether external sorting was activated, and deletes entries from the map as callbacks arrive. The temp-file test forces external-sort initialization against an unwritable or invalid directory and expects an error.

## State and persistence behavior
Most tests use in-memory maps and mock entries. The temp-file test creates temporary filesystem paths and permission states, with cleanup on Unix. External-sort tests may create temporary files through the library when cutoff is exceeded.

## Dependencies and integration points
The tests use rclone config `ListCutoff`, mock object/dir packages, Go runtime path behavior, and OS temp/permission semantics. They protect `DirSortedFn` and `march` because both rely on deterministic sorted entry streams.

## Risks and edge cases
The external-sort path depends on re-fetching objects by remote and distinguishing directories by a trailing slash in serialized data. The test type-check assertions have a minor local bug (`gotDir`/`gotObj` are derived from `wantEntry`), but map deletion and callback order still catch many failures.

## Test signals
Coverage is strong for sorting order, case-insensitive key functions, cutoff values exactly around 100000 entries, cleanup state, and the no-panic error path when temporary file creation fails.

Source-read signal: reviewed complete local file (362 lines). Types observed: `testFs`, `benchFs`. Functions/methods observed: `TestSorter`, `TestSorterIdentity`, `TestSorterKeyFn`, `NewObject`, `String`, `keyCaseInsensitive`, `testSorterExt`, `TestSorterExt`, `TestSorterExtTempFileError`, `NewObject`, `String`, `BenchmarkSorterExt`.
