# sources/sync-backup/borg/src/borg/helpers/datastruct.py

## Purpose
Provides small reusable data structures: deterministic dict iteration, managed buffers with limits, and a chunked FIFO queue.

## Important APIs, Types, And Functions
`StableDict.items()` returns sorted items for stable serialization. `Buffer` manages an allocator-backed buffer with `resize` and `get`; `Buffer.MemoryLimitExceeded` is both `Error` and `OSError`. `EfficientCollectionQueue` maintains FIFO data split across member-type chunks; it provides `peek_front`, `pop_front`, `push_back`, `__len__`, and `__bool__`, plus `SizeUnderflow`.

## Control Flow
`Buffer.get` optionally resizes before returning the current buffer; normal growth only reallocates when the requested size exceeds the current buffer, while `init=True` permits shrinking/reinitialization. `EfficientCollectionQueue.push_back` appends into the last chunk until `split_size`, then creates new member collections. `pop_front` removes across chunks and deletes exhausted buffers.

## State And Persistence
All state is in-memory. `Buffer` stores `allocator`, `limit`, and `buffer`. `EfficientCollectionQueue` tracks `buffers`, total `size`, `split_size`, and `member_type`.

## Dependencies And Integration Points
`StableDict` is used by msgpack limited unpackers and legacy manifest output for deterministic ordering. `Buffer` is useful for low-level IO and crypto/compression paths. `EfficientCollectionQueue` has dedicated tests and supports stream assembly behavior.

## Risks And Edge Cases
`Buffer.__init__` asserts initial size does not exceed limit; assertions may be optimized out under `-O`. `push_back` relies on `member_type` supporting empty construction, slicing, concatenation, and length. `pop_front` raises for underflow before mutating, which is important for callers.

## Test Signals
Existing tests should cover stable ordering, allocator call counts, limit exceptions, shrink behavior with `init=True`, queue chunk boundaries, peeking empty/non-empty queues, multi-buffer pops, and underflow.
