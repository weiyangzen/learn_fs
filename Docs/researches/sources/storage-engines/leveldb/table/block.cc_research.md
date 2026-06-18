# sources/storage-engines/leveldb/table/block.cc

## Purpose
`block.cc` decodes LevelDB table data/index blocks produced by `BlockBuilder`, exposing ordered key/value iteration over prefix-compressed entries.

## Important APIs, Types, and Functions
`Block::Block`, `Block::~Block`, `Block::NewIterator`, private `Block::NumRestarts`, helper `DecodeEntry`, and nested `Block::Iter` implement parsing, seeking, forward/reverse movement, and corruption reporting.

## Control Flow
Construction validates the trailer and restart array bounds. `NewIterator` returns an error iterator for malformed blocks, an empty iterator for zero restarts, or `Block::Iter`. `Iter::Seek` binary-searches restart points, then linearly scans within a restart region. `Next` parses the next delta-compressed key. `Prev` backs up to the previous restart and scans forward to the entry before the original offset.

## State, Persistence, and Integration
`Block` may own heap data read by `ReadBlock`. Iteration state includes current offset, restart index, reconstructed key, value slice, and status. It integrates with `Table`, `TwoLevelIterator`, table tests, and block cache cleanup. No persistence is written here; it interprets persisted SSTable blocks.

## Risks and Test Signals
Malformed restart offsets, shared-prefix lengths exceeding the current key, truncated varints, and comparator ordering bugs all surface as corruption or invalid iteration. Tests exercise empty blocks, zero restart points, random forward/backward seeks, custom comparators, and table round trips.
