# sources/user-network-fs/rclone/fs/operations/dedupe_test.go

## Purpose
`dedupe_test.go` validates the duplicate-file and duplicate-directory behavior implemented by `dedupe.go` across supported backend features.

## Important APIs, types, and functions
- The compile-time assertion ensures `DeduplicateMode` satisfies `pflag.Value`.
- `skipIfCantDedupe`, `skipIfNoHash`, and `skipIfNoModTime` gate backend-dependent scenarios.
- Tests cover all selection modes: interactive, skip, first, newest, oldest, largest, smallest, rename, and newest by hash.
- `TestMergeDirs` directly validates backend `MergeDirs` behavior used by directory dedupe.

## Control flow
Tests create duplicate objects using `WriteUncheckedObject` where backends support duplicate files. They then call `operations.Deduplicate` with a specific mode and assert resulting remote listings through `CheckRemoteItems`, `CheckWithDuplicates`, `operations.Count`, or `walk.ListR`. Selection tests vary content size and modtime so the expected survivor is identifiable.

## State and persistence behavior
The tests mutate temporary remote state by creating duplicate files, deleting duplicates through the operation under test, renaming duplicates, and merging directories. `TestDeduplicateSizeOnly` temporarily sets `ci.SizeOnly` and restores it afterward.

## Dependencies and integration points
The file depends on backend feature flags, `fs/hash`, `operations`, `walk`, `fstest`, random content generation, `pflag`, and `testify`. It primarily tests `Deduplicate` but also exercises shared deletion and counting helpers.

## Risks and edge cases
Most tests are skipped unless the selected backend can represent duplicates and supports `PutUnchecked`, `MergeDirs`, hashes, or modtimes as needed. The first-mode test polls count because duplicate deletion may be eventually consistent. Rename tests verify existing non-duplicate numbered names are preserved.

## Test signals
The scenarios confirm that identical duplicates can be removed before mode-specific decisions, size-only mode groups by size, by-hash mode can dedupe same content at different paths, rename mode avoids collisions, and directory merge consolidates children into one directory.
