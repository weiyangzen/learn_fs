# sources/user-network-fs/rclone/fs/operations/lsjson_test.go

## Purpose
`lsjson_test.go` validates JSON listing and stat conversion for files, directories, recursion, optional fields, hash maps, metadata, and not-found behavior.

## Important APIs, types, and functions
- `compareListJSONItem` compares expected and actual `ListJSONItem` values with backend precision-aware modtime checks.
- `TestListJSON` exercises `operations.ListJSON` option combinations.
- `TestStatJSON` exercises `operations.StatJSON` for root, files, directories, trailing slashes, not-found paths, and file/dir filters.

## Control flow
The tests create two files, one at root and one in a subdirectory, then run table-driven scenarios. `ListJSON` callbacks collect items, sort by path, compare structural fields, and assert optional MIME, metadata, and hash behavior. `StatJSON` table scenarios call the single-entry API and compare nil or non-nil results.

## State and persistence behavior
Tests create temporary files on local and remote test backends. They do not mutate global config beyond what `fstest` requires. Assertions adapt to backend features such as metadata support, bucket-based roots, and available hashes.

## Dependencies and integration points
The file depends on `fs`, `operations`, `fstest`, `testify`, sorting, and precision helpers. It directly tests `lsjson.go` and indirectly checks backend metadata/hash implementations through optional assertions.

## Risks and edge cases
Hash expectations are conditional because different backends expose different hash families. Metadata assertions are feature-gated for files and directories. Root stat can return an error for non-bucket backends when the target root does not exist, while bucket-based backends may not.

## Test signals
The tests confirm `FilesOnly` and `DirsOnly` filtering, recursion depth, subdirectory listing, omitted modtime/MIME fields, hash selection, metadata population, root directory representation, trailing slash directory lookup, and nil results for filtered or missing entries.
