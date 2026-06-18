# sources/user-network-fs/rclone/fs/list/list_test.go

## Purpose
`list_test.go` validates filtering, sorting, and directory-membership checks used by `list.go`.

## Important APIs, types, and functions
Tests focus on unexported `filterAndSortDir` and the `unknownDirEntry` mock type. They indirectly exercise `filterDir` and stable sorting of `fs.DirEntries` by remote.

## Control flow
`TestFilterAndSortIncludeAll` builds mixed mock directories/objects and compares includeAll behavior against filtered object/directory predicates. `TestFilterAndSortCheckDir` and root variants feed intentionally malformed remotes to ensure only direct children remain. `TestFilterAndSortUnknown` verifies non-object/non-directory entries return an error.

## State and persistence behavior
Tests use only in-memory mock entries. No persistent state or filesystem state is touched.

## Dependencies and integration points
The suite uses `mockdir`, `mockobject`, `fs.DirEntries`, context, and testify. It protects the listing contract consumed by sync, walk, and backend wrappers.

## Risks and edge cases
The tests encode allowed double-slash/bucket-style directory exceptions and reject entries with wrong prefixes, same name as the directory, or nested children. Filter callback errors are not covered here.

## Test signals
Coverage is concise but covers the main correctness risks: stable output order, includeAll bypassing filters, filtered exclusions, root versus subdirectory validation, and unknown entry-type failures.

Source-read signal: reviewed complete local file (108 lines). Types observed: `unknownDirEntry`. Functions/methods observed: `TestFilterAndSortIncludeAll`, `TestFilterAndSortCheckDir`, `TestFilterAndSortCheckDirRoot`, `Fs`, `String`, `Remote`, `ModTime`, `Size`, `TestFilterAndSortUnknown`.
