# sources/storage-engines/rocksdb/table/block_based/full_filter_block.h

## Purpose
Declares full-filter builder and reader classes for block-based tables. Full filters store one filter block covering the whole SST file and expose key/prefix maybe-match APIs to point lookup, multi-get, and range logic.

## Important APIs, Types, And Functions
`FullFilterBlockBuilder` derives from `FilterBlockBuilder` and exposes construction with a prefix extractor, whole-key flag, and owned `FilterBitsBuilder`. It overrides add, finish, estimate, data-block-finalization, reset, and post-verification methods. `FullFilterBlockReader` derives from `FilterBlockReaderCommon<ParsedFullFilterBlock>` and exposes `Create`, single-key/prefix methods, batch key/prefix methods, `KeysMayMatch2`, and memory accounting.

## Control Flow
Table construction creates a builder from table filter policy context, feeds all keys to it, and writes the returned full filter as a meta block. Table reading creates a full-filter reader around a cached/pinned/lazy parsed block. Point and prefix queries delegate into a private `MayMatch` helper.

## State And Persistence Behavior
The builder owns `filter_bits_builder_` and may own `filter_data_` after finishing. The reader owns or references a `ParsedFullFilterBlock` through the base class. Durable format is selected by the underlying filter policy, not by the wrapper itself.

## Dependencies And Integration Points
Depends on filter interfaces, internal filter policy declarations, parsed full filter blocks, prefix extractors, block cache context, and block-based table reader state. It integrates with full-filter table options and with partitioned filter code through the compatible `KeysMayMatch2` helper.

## Risks And Edge Cases
The builder stores raw pointers to prefix extractor configuration that must outlive the builder but are not dereferenced in destruction. `ResetFilterBitsBuilder` makes later post-verification invalid if called too early. `whole_key_filtering` determines whether keys outside prefix-domain still produce filter entries.

## Test Signals
Full-filter tests validate empty behavior, custom plugin policies, duplicate/prefix counting, and both positive and negative may-match results.
