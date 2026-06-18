# sources/storage-engines/rocksdb/db/read_callback.h

## Purpose

`read_callback.h` declares the `ReadCallback` abstraction used by RocksDB read paths that need custom sequence-number visibility checks, especially transaction-aware reads where some committed/uncommitted boundaries are more nuanced than a plain snapshot sequence.

## Important APIs and Types

`ReadCallback` stores `max_visible_seq_` and `min_uncommitted_`. Constructors accept either just the last visible sequence or both the last visible sequence and the minimum uncommitted sequence. Subclasses must implement `IsVisibleFullCheck(SequenceNumber seq)`. Inline `IsVisible(seq)` applies the fast path, and `Refresh(seq)` updates the maximum visible sequence.

## Control Flow and State Behavior

`IsVisible` first asserts a valid `min_uncommitted_`. Any sequence below `min_uncommitted_`, including sequence zero, is treated as committed and visible, with an assertion that it does not exceed the max visible sequence. A sequence above `max_visible_seq_` is invisible. Only the uncertain middle range calls the virtual `IsVisibleFullCheck`, allowing transaction implementations to decide visibility for prepared or uncommitted writes.

`Refresh` defaults to assigning a newer maximum visible sequence, letting callers advance a read view without replacing the callback object.

## Persistence, Dependencies, and Integration

This header has no persistence behavior. It depends on `dbformat` constants such as `kMinUnCommittedSeq` and sequence-number types. Integration points are DB/memtable/table read loops that test whether an internal key sequence should be visible under snapshots, transactions, or write-prepared/write-unprepared modes.

## Risks and Test Signals

The main risk is misuse of `min_uncommitted_` or `max_visible_seq_`, since the fast path bypasses the virtual check for all committed-below-min sequences. Implementations must ensure `IsVisibleFullCheck` is correct for the uncertain range. This file has no direct tests in the subset; coverage is likely through transaction and DB iterator suites that include prepared/uncommitted visibility.
