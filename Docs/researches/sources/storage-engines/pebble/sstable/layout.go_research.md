# sources/storage-engines/pebble/sstable/layout.go

## Purpose
Describes, decodes, formats, and writes the physical block layout of an SSTable, including data/index/meta/filter/range/value/blob/tiering/footer blocks.

## Important APIs, Types, and Functions
- `Layout` records block handles by role plus table format.
- `NamedBlockHandle` names handles for ordering and display.
- `Layout.orderedBlocks` and `Layout.Describe` produce physical-layout descriptions.
- Formatting helpers handle row/columnar data/index/keyspan blocks, properties, metaindex, value/blob/tiering metadata, and footers.
- `decodeLayout`, `decompressInMemory`, `newIndexIter`, `forEachIndexEntry`, `decodeMetaindex`, and `decodeColumnarMetaIndex` reconstruct layout from bytes.
- `layoutWriter` writes physical blocks, records metaindex entries, clears cache collisions, and finalizes metaindex/footer.
- Writer methods include `WriteDataBlock`, `WritePrecompressedDataBlock`, `WriteIndexBlock`, `WriteFilterBlock`, `WritePropertiesBlock`, `WriteRangeKeyBlock`, `WriteBlobRefIndexBlock`, `WriteTieringHistogramBlock`, `WriteRangeDeletionBlock`, `WriteValueBlock`, `WriteValueIndexBlock`, `Finish`, and `Abort`.

## Control Flow
Layout description sorts all known blocks by offset and optionally reads/decompresses each block for verbose formatting. Layout decoding parses the footer, decodes row or columnar metaindex, reads properties to detect one- vs two-level index, walks index entries to collect data handles, and decodes value block index handles. `layoutWriter` writes blocks sequentially, records named metaindex handles, writes a row or columnar metaindex depending on format, encodes the footer, finishes the writable, and closes compression resources.

## State and Persistence Behavior
This file defines the order and metadata linkage of persisted SSTable blocks. Formats v6+ use columnar metaindex blocks; v7+ may use compressed columnar properties and footer attributes. Named blocks are stored in the metaindex, while the footer stores metaindex and last index handles plus checksum/attributes/version/magic. `layoutWriter.offset` is the authoritative current file offset.

## Dependencies and Integration Points
Central integration point for `Reader`, `RawColumnWriter`, `CopySpan`, compression analyzer, block readers/writers, `footer`, `Attributes`, `valblk`, `blob`, `tieredmeta`, row/columnar block packages, and object storage. The layout description path is used heavily by datadriven tests.

## Risks and Edge Cases
Handle decoding must match row/columnar metaindex format and special value-index handle encoding. Footer checksum/attributes offsets are format-specific. Cache clearing is defensive against cache key collisions. Optional handles with zero length must be skipped by callers. Verbose formatting must not leak buffers and must release block handles.

## Test Signals
Exercised by `colblk_writer_test.go`, copier tests, file analyzer tests, and many reader/writer datadriven suites that compare `Layout.Describe` output.
