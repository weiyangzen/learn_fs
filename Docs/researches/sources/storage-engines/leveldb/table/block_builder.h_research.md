# sources/storage-engines/leveldb/table/block_builder.h

## Purpose
`block_builder.h` declares the block serialization helper used by table writing and meta/index block construction.

## Important APIs, Types, and Functions
`BlockBuilder` exposes `Reset`, `Add`, `Finish`, `CurrentSizeEstimate`, and `empty`. Private state includes `options_`, `buffer_`, `restarts_`, `counter_`, `finished_`, and `last_key_`.

## Control Flow
Clients repeatedly add ordered key/value slices, optionally check size estimates, finish to receive a slice into the internal buffer, then reset for reuse.

## State, Dependencies, and Integration
The builder references external `Options`; it does not own them. `TableBuilder` relies on this for data blocks, index blocks, and metaindex blocks. The returned `Slice` is valid only until reset or destruction.

## Risks and Test Signals
Lifetime coupling of `Options` and returned slices is important. Tests indirectly validate format compatibility through `Block` and `Table` round trips.
