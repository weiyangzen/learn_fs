# sources/storage-engines/leveldb/table/filter_block.h

## Purpose
`filter_block.h` declares builder and reader classes for table-level filter metadata.

## Important APIs, Types, and Functions
`FilterBlockBuilder` exposes `StartBlock`, `AddKey`, and `Finish`; `FilterBlockReader` exposes `KeyMayMatch`. The builder stores flattened keys, key offsets, output bytes, temporary slices, and filter offsets. The reader stores pointers into a caller-owned contents slice.

## Control Flow
Table writing calls `StartBlock` when a data block starts and `AddKey` for each data key. Table reading constructs a reader from the filter meta block and asks whether a key may exist in a data block.

## State, Dependencies, and Integration
Both classes depend on a live `FilterPolicy`. `FilterBlockReader` also requires the underlying filter bytes to outlive it, which `Table::Rep` satisfies through `filter_data`.

## Risks and Test Signals
Lifetime of policy and contents is the main integration risk. Filter block tests verify block-offset mapping and empty-filter behavior.
