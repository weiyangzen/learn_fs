# sources/storage-engines/leveldb/table/two_level_iterator.cc

## Purpose
`two_level_iterator.cc` flattens an index iterator whose values identify data blocks into one logical key/value iterator.

## Important APIs, Types, and Functions
`TwoLevelIterator` implements full `Iterator` navigation. Key helpers are `InitDataBlock`, `SetDataIterator`, `SkipEmptyDataBlocksForward`, `SkipEmptyDataBlocksBackward`, and `SaveError`. `NewTwoLevelIterator` constructs it.

## Control Flow
Seek operations position the index iterator, instantiate the corresponding data iterator through `block_function`, seek inside it, and skip empty blocks. `Next`/`Prev` advance the current data iterator and move across index entries when exhausted. Reusing `data_block_handle_` avoids rebuilding the data iterator for the same block.

## State, Persistence, and Integration
It owns an index iterator and current data iterator through `IteratorWrapper`, stores read options and an accumulated error status, and calls `Table::BlockReader` for table iteration. It writes no persistent state.

## Risks and Test Signals
Backward skipping is delicate because it calls `index_iter_.Prev()` after invalid data blocks. Error preservation depends on `SetDataIterator`. Table tests exercise cross-block seeking and direction changes.
