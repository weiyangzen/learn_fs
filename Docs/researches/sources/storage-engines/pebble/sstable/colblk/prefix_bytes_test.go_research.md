<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/sstable/colblk/prefix_bytes_test.go -->
# sources/storage-engines/pebble/sstable/colblk/prefix_bytes_test.go

## Purpose
`prefix_bytes_test.go` validates the prefix-compressed byte-slice column encoding. It checks binary layout, reconstruction, search behavior, row truncation, builder reset, `UnsafeGet`, and performance.

## Important APIs, Types, And Functions
`TestPrefixBytes` is datadriven over `testdata/prefix_bytes`. `TestPrefixBytesRandomized` generates sorted key sets and verifies round trips. `TestPrefixBytesBuilder_UnsafeGet` stresses last and second-last key retrieval. `BenchmarkPrefixBytes` measures build and iteration costs. Test helpers include `debugString` and `wrapStr`.

## Control Flow
Datadriven commands initialize a builder with bundle size, put sorted keys while computing shared prefix length from the previous key, call `UnsafeGet`, finish a chosen row count into a buffer with an extra byte for checkptr safety, decode and format the result, reconstruct selected keys through `SharedPrefix`/`RowBundlePrefix`/`RowSuffix`, search keys, and list bundle prefixes. Randomized tests create keys with a common block prefix, sort them, choose bundle sizes, sometimes call `Reset`, sometimes finish all but the last key, decode, reconstruct keys in random order, and verify `Search` finds an equal row.

## State And Persistence Behavior
The tests persist encoded prefix bytes into byte slices, explicitly adding one trailing byte outside the column to satisfy Go pointer rules during standalone column tests. They record size after each row to test row-count-specific finishing. Randomized reset paths verify retained builder state does not leak into subsequent encodings.

## Dependencies And Integration Points
The tests use `datadriven`, `crbytes.CommonPrefix`, `binfmt`, `treeprinter`, `testkeys`, `invariants`, and `testify/require`. They directly cover the encoding used by `DefaultKeySchema` in data blocks.

## Risks
Randomized tests use time seeds and should log the seed for reproduction. They mostly generate lowercase byte keys and do not intentionally feed malformed unsorted or empty keys outside invariant panic paths. The benchmark's invariant equality checks run only when invariants are enabled.

## Test Signals
Signals include golden debug formatting, exact size/finish agreement, decoded end offsets, successful key reconstruction, search equality for duplicates, `UnsafeGet` correctness for duplicate versions, and benchmark metrics for build and sequential iteration.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/sstable/colblk/prefix_bytes_test.go -->
