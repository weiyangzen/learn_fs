<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/sstable/colblk/prefix_bytes.go -->
# sources/storage-engines/pebble/sstable/colblk/prefix_bytes.go

## Purpose
`prefix_bytes.go` implements the `PrefixBytes` column encoding for lexicographically sorted byte slices. It compresses one block-wide shared prefix, one prefix per fixed-size bundle, and per-row suffixes, with duplicate keys represented as empty row slices.

## Important APIs, Types, And Functions
`PrefixBytes` implements `Array[[]byte]` and exposes `DecodePrefixBytes`, `At`, `UnsafeFirstSlice`, `SharedPrefix`, `RowBundlePrefix`, `BundlePrefix`, `RowSuffix`, `Rows`, `BundleCount`, and `Search`. `PrefixBytesIter` provides reusable buffer materialization through `Init`, `SetAt`, and `SetNext`. `PrefixBytesBuilder` implements `ColumnWriter` with `Init`, `Reset`, `Rows`, `Put`, `UnsafeGet`, `Finish`, `Size`, and `WriteDebug`. Helpers include `prefixBytesSizing`, `writePrefixCompressed`, and `bundleCalc`.

## Control Flow
Builders ingest sorted keys through `Put(key, bytesSharedWithPrev)`. The first key initializes placeholder offsets and sizing metadata. Starting a new bundle finalizes the previous bundle prefix offset and compressed size, potentially shrinks the block prefix, and starts new placeholders. Within a bundle, duplicate keys append an unchanged offset, while distinct keys update current bundle prefix length and compressed sizing. `Finish` writes the bundle shift byte, a uint-encoded offset table, and compressed string data through width-specialized `writePrefixCompressed`. Decoding reads the bundle shift, computes total logical slices, decodes a modified `RawBytes`, and records shared-prefix length.

## State And Persistence Behavior
Persistent state starts with one byte storing `log2(bundleSize)`, followed by a modified raw-bytes encoding of `1 + bundleCount + rows` slices. Offset zero stores the length of the block-wide prefix instead of an implicit zero. Builder state keeps raw uncompressed concatenated keys, offset placeholders, two rolling `prefixBytesSizing` records for `n` and `n-1` finishing, completed bundle length, bundle geometry, and max shared-prefix length. Decoded accessors return slices into block memory; `At` allocates by concatenating prefix components.

## Dependencies And Integration Points
The encoding is used by `DefaultKeySchema` for user-key prefixes and by generic block tests. It depends on `RawBytes`, uint encoders, unsafe allocation/copy helpers, `crbytes.CommonPrefix`, `binfmt`, `treeprinter`, and `blockiter.SyntheticPrefix` for iterator buffers.

## Risks
The format assumes non-empty sorted keys and power-of-two bundle sizes. Search is subtle around duplicate empty row slices, bundle-boundary comparisons, and block-prefix mismatches. `PrefixBytesIter` relies on callers allocating enough capacity based on maximum key length plus synthetic transforms. `UnsafeGet` only supports the last two keys and panics otherwise. Size/finish support for `Rows()` or `Rows()-1` depends on rolling sizing state staying correct.

## Test Signals
`prefix_bytes_test.go` provides datadriven format/search/get coverage, randomized reconstruction and search checks across many sizes and alphabets, `UnsafeGet` checks, and build/iteration benchmarks. Generic block tests also exercise prefix bytes as a column type.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/sstable/colblk/prefix_bytes.go -->
