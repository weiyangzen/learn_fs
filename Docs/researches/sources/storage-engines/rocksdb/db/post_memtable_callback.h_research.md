# sources/storage-engines/rocksdb/db/post_memtable_callback.h

## Purpose
`post_memtable_callback.h` declares `PostMemTableCallback`, an internal write-path callback invoked after a write has been applied to the memtable but before the sequence number is published to readers.

## Important APIs, Types, And Functions
`PostMemTableCallback` is an abstract class with a virtual destructor and pure virtual `Status operator()(SequenceNumber seq, bool disable_memtable)`.

The parameters expose the sequence number associated with the write and whether the memtable is disabled. The return `Status` allows the callback to signal failure to the write path.

## Control Flow
Write-path code can accept an implementation of this callback and invoke it at the post-memtable/pre-publication point. Implementations perform their side effect and return OK or an error.

## State And Persistence Behavior
The header contains no state. Implementations may update external state while the write is not yet visible to readers. Because invocation happens after memtable insertion, callback failure semantics must be coordinated carefully by the write path.

## Dependencies And Integration Points
The header depends on `rocksdb/status.h` and `rocksdb/types.h` for `Status` and `SequenceNumber`. It integrates with RocksDB write queues, memtable insertion, and sequence-number publication. The comment notes write-prepared/write-unprepared transactions with two write queues call `PreReleaseCallback` before publishing sequence numbers to readers, clarifying ordering with the sibling callback type.

## Risks
Callbacks run in a sensitive visibility window. A slow callback delays sequence publication; a failed callback after memtable insertion needs write-path handling that avoids exposing inconsistent state. Implementations must understand `disable_memtable` semantics, which are tied to write queue modes.

## Test Signals
Relevant tests would assert callback ordering relative to memtable writes and sequence publication, propagation of non-OK status, and correct behavior in write-prepared/write-unprepared transaction modes.
