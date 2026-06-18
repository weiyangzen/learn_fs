# sources/user-network-fs/rclone/fs/list/list.go

## Purpose
`list.go` implements filtered and sorted directory listing for rclone operations. It wraps backend `List`, `ListP`, and optional `ListR` behavior with accounting, filter evaluation, directory membership validation, and stable sorting.

## Important APIs, types, and functions
Public APIs are `DirSorted` and `DirSortedFn`. Internal helpers are `listP`, `filterDir`, and `filterAndSortDir`. `DirSortedFn` uses the external-capable `Sorter` from `sorter.go` and accepts a `KeyFn` for custom ordering.

## Control flow
`DirSorted` calls `f.List`, counts entries, optionally rejects an exclude-file directory, filters entries, and stable-sorts in memory. `DirSortedFn` creates a `Sorter`, lists via `ListP` if available or `List` fallback, counts entries per callback, filters each batch, adds it to the sorter, and finally sends sorted results. `filterDir` checks object and directory filters, validates that each remote belongs directly to the listed directory, and logs ignored malformed entries.

## State and persistence behavior
The functions hold transient entry slices and sorter state. They update listing accounting counters and read filter/config state from context. They do not persist changes.

## Dependencies and integration points
Dependencies include `fs.Fs`, optional `Features().ListP`, `accounting`, `filter`, `bucket.IsAllSlashes`, and `Sorter`. This code feeds operations such as sync/copy/check that require deterministic directory listings.

## Risks and edge cases
Backends can return malformed entries, duplicate entries, entries outside the requested dir, same-as-dir entries, or nested children in non-recursive listings; this code filters/logs those. Exclude-file handling only applies when listing the starting directory. Sorting must be stable to preserve backend order for duplicates.

## Test signals
`list_test.go` covers includeAll versus filtered listing, directory-membership validation at normal and root dirs, bucket slash exceptions, and erroring on unknown `DirEntry` types. Integration tests elsewhere cover `DirSorted` through operations.

Source-read signal: reviewed complete local file (177 lines). Functions/methods observed: `DirSorted`, `listP`, `DirSortedFn`, `filterDir`, `filterAndSortDir`.
