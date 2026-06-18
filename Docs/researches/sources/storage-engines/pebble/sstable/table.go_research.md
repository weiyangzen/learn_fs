# sources/storage-engines/pebble/sstable/table.go

## Purpose
Defines the SSTable package overview, on-disk table layout documentation, footer constants and parsing/encoding logic, and a helper for two-level-index support by table format.

## Important APIs, Types, And Functions
The central type is unexported `footer`, containing table format, attributes, checksum type, metaindex handle, index handle, and footer handle. Functions are `readFooter`, `parseFooter`, `footer.encode`, and `supportsTwoLevelIndex`. The file also declares block handle sizing constants, checksum/magic/version/footer sizes, meta block names, index type constants, and table magic strings.

## Control Flow And State
`readFooter` reads up to the maximum footer length from the end of an `objstorage.Readable`, validates minimum size, and delegates to `parseFooter`. `parseFooter` dispatches on magic bytes for LevelDB, RocksDB, and Pebble footers; determines table format from magic/version; selects footer length; validates checksum type; verifies Pebblev6+ footer CRC; reads Pebblev7 attributes; decodes metaindex and index block handles; and rejects handles extending beyond file size.

`footer.encode` writes the corresponding footer format: zeroed padding, checksum type, encoded block handles, format version, magic, optional attributes, and optional CRC over footer bytes with the checksum field skipped. `supportsTwoLevelIndex` allows two-level indexes for RocksDBv2 and Pebble formats but not LevelDB.

## Persistence And Integration
This file documents and implements persistent SSTable footer compatibility across LevelDB, RocksDB, and Pebble formats. It is used by readers to locate metaindex and index blocks and by writers/layout code to finalize table files. The layout comment also defines how row blocks, restart points, data-block v3 value prefixes, restart high bits, and v4 obsolete bits are interpreted by `rowblk.Writer` and `rowblk.Iter`.

## Dependencies
Depends on `objstorage` for reads, `block.ReadRaw` and block handle encoding/decoding, `crc` for footer checksums, `base` for corruption errors/logging/file numbers, and table-format helpers defined elsewhere in the `sstable` package.

## Risks
Footer parsing is compatibility-critical. Incorrect footer-size, magic, version, checksum offset, or handle-bound validation can make valid tables unreadable or accept corrupt tables. Pebblev7 attributes must be checksummed consistently. The package comment is also a contract for row-block encoding, so changes in `rowblk` must remain aligned with this documentation.

## Test Signals
Tests for footer parsing and table format compatibility are outside this subset. In this work item, row-block writer/iterator tests and suffix-rewriter tests indirectly validate the documented row-block and table layout assumptions by writing and reading in-memory SSTables.
