# sources/storage-engines/pebble/sstable/copier_test.go

## Purpose
Datadriven integration tests for block-level SSTable span copying.

## Important APIs, Types, and Functions
- `TestCopySpan` builds an in-memory filesystem, cache, key schema, and file-number mapping.
- `getReader` opens SSTables with cache and bloom filter decoder options.
- Commands include `build`, `iter`, `copy-span`, `describe`, and `props`.

## Control Flow
`build` writes a test SSTable with small block size to create many blocks. `iter` opens and scans a file with optional bounds. `copy-span` opens a reader and a separate readable for `CopySpan`, writes output to the memory FS, and reports copied size. `describe` prints non-verbose layout, and `props` prints properties.

## State and Persistence Behavior
All files live in `vfs.NewMem`. Cache handles are configured with per-file numbers to exercise cache hit/miss behavior. Output files are added back into the same memory filesystem for subsequent inspection.

## Dependencies and Integration Points
Uses `datadriven`, `objstorageprovider`, `NewWriter`, `NewReader`, `CopySpan`, `Layout.Describe`, bloom filter decoding, `testkeys`, and columnar key schemas.

## Risks and Edge Cases
The test relies on small block sizes to make copy behavior visible. It covers observable behavior but does not directly assert internal cache-hit grouping decisions.

## Test Signals
Good end-to-end signal for partial block copying, output readability, layout preservation, and property behavior.
