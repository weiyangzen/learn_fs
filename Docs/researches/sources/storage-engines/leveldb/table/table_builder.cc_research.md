# sources/storage-engines/leveldb/table/table_builder.cc

## Purpose
`table_builder.cc` writes immutable SSTable files from sorted key/value pairs.

## Important APIs, Types, and Functions
`TableBuilder::Add`, `Flush`, `WriteBlock`, `WriteRawBlock`, `ChangeOptions`, `Finish`, `Abandon`, `status`, `NumEntries`, and `FileSize` operate over `TableBuilder::Rep`.

## Control Flow
`Add` enforces sorted keys, resolves any pending index entry using `FindShortestSeparator`, adds keys to the filter, appends to the data block, and flushes when the size estimate exceeds `block_size`. `Flush` writes a data block and starts a new filter region. `WriteBlock` may Snappy/Zstd compress if the output is at least 12.5% smaller, then writes raw bytes plus type and masked CRC trailer. `Finish` writes filter block, metaindex block, index block, and footer.

## State, Persistence, and Integration
State includes mutable options, file offset, data/index block builders, last key, pending block handle, optional filter builder, compressed output buffer, and status. Output is the durable table format read by `Table::Open`.

## Risks and Test Signals
Sorted input is asserted, not returned as status. Calling neither `Finish` nor `Abandon` trips the destructor assert. Compression support is optional and silently falls back to uncompressed. Tests validate file size, iteration, offsets, and compression behavior.
