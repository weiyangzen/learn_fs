# sources/storage-engines/leveldb/table/format.h

## Purpose
`format.h` declares the stable SSTable low-level format abstractions: block handles, footer layout, block trailer constants, and block contents.

## Important APIs, Types, and Functions
`BlockHandle` stores `offset_` and `size_`; `Footer` stores metaindex and index handles. `BlockContents` carries read bytes plus ownership/cacheability flags. `ReadBlock` is declared for table reads.

## Control Flow
Writers encode handles and footers at table finalization. Readers decode footer bytes from the end of a file, then use handles to read blocks.

## State, Dependencies, and Integration
The file depends on `Slice`, `Status`, `RandomAccessFile`, `ReadOptions`, and table builder compression constants. It is a contract between `table_builder.cc`, `table.cc`, and `block.cc`.

## Risks and Test Signals
Because `Footer::kEncodedLength` is fixed, any incompatible change is an on-disk format change. Tests validate file size, approximate offsets, and table opening.
