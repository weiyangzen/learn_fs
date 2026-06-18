# sources/user-network-fs/rclone/fs/operations/listdirsorted_test.go

## Purpose
`listdirsorted_test.go` provides integration tests for `fs/list` directory sorting behavior from the operations test package to avoid import cycles in the list package itself.

## Important APIs, types, and functions
- `testListDirSorted` is a shared scenario runner for list functions.
- `TestListDirSorted` tests `list.DirSorted`.
- `TestListDirSortedFn` adapts and tests `list.DirSortedFn`.

## Control flow
The shared test creates a fixture tree with files, nested directories, and an `.ignore` file. It toggles `filter.GetConfig(ctx).Opt.MaxSize` and later `ExcludeFile`, then lists root and subdirectories with `includeAll` both true and false. It converts returned entries to strings with trailing `/` for directories and asserts sorted order and filtering behavior.

## State and persistence behavior
The file writes temporary test objects through `fstest.NewRun`. It mutates global filter options (`MaxSize` and `ExcludeFile`) during the test and resets them. No repository files are persisted.

## Dependencies and integration points
The tests integrate `fs/list` with `fs/filter`, `fstest`, and the operations test package. They indirectly validate behavior relied on by listing and sync operations that expect sorted, filter-aware directory entries.

## Risks and edge cases
The key edge cases are size filtering, include-all bypass behavior, directory ordering, nested ignore-file behavior, and ensuring `DirSortedFn` and `DirSorted` stay equivalent. Filter globals must be reset to avoid leaking state into later tests.

## Test signals
Expected results show that include-all lists files even when normal filtering excludes them, directories remain visible when they may contain included children, `.ignore` can suppress a directory's contents, and both list APIs produce identical sorted output.
