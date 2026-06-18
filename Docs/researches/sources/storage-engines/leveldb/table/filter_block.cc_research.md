# sources/storage-engines/leveldb/table/filter_block.cc

## Purpose
`filter_block.cc` builds and reads SSTable filter blocks, grouping keys by 2 KiB data-file offset regions to avoid unnecessary data block reads.

## Important APIs, Types, and Functions
`FilterBlockBuilder::StartBlock`, `AddKey`, `Finish`, `GenerateFilter`, and `FilterBlockReader::KeyMayMatch` implement the format. Constants `kFilterBaseLg` and `kFilterBase` define the 2 KiB mapping.

## Control Flow
`StartBlock` computes the target filter index from data block offset and emits empty filters until caught up. `AddKey` appends flattened key bytes and start offsets. `GenerateFilter` materializes `Slice` views and delegates encoding to `FilterPolicy::CreateFilter`. `Finish` appends filter offsets, offset-array start, and base logarithm. The reader decodes the trailer and uses per-filter offsets to call `FilterPolicy::KeyMayMatch`, treating malformed or out-of-range data as a possible match.

## State, Persistence, and Integration
Builder state is serialized as one meta block referenced by `TableBuilder` under `filter.<policy name>`. `Table::InternalGet` consults the reader before opening a data block. The filter block is durable table metadata.

## Risks and Test Signals
False negatives would be correctness bugs, so corrupt or unknown filter bytes deliberately return true. Tests cover empty builders, single filter chunks, multiple chunks, and empty filter intervals.
