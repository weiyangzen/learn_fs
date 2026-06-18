# sources/storage-engines/rocksdb/db/history_trimming_iterator.h

Defines `HistoryTrimmingIterator`, a thin `InternalIterator` wrapper that skips records whose user-defined timestamp is newer than a configured cutoff. It is used where RocksDB needs to trim historical versions according to timestamp history retention.

The constructor takes an input `InternalIterator*`, a timestamp-aware `Comparator*`, and a non-empty cutoff timestamp string. `filter()` extracts the current key timestamp with `ExtractTimestampFromKey()` and keeps entries whose timestamp compares less than or equal to `filter_ts_`. The class forwards `Valid()`, `key()`, `value()`, `status()`, pinning checks, delete-range sentinel checks, and movement to the input iterator.

Each seek method positions the child and then advances in the same direction until `filter()` returns true. `Next()` and `Prev()` always move once, then continue past newer-than-cutoff entries. If the child becomes invalid, `filter()` returns true so loops stop.

There is no persistent state and no ownership of the input pointer. Runtime state is the input iterator pointer, copied cutoff timestamp, and comparator pointer. The wrapper hides entries but does not rewrite keys or values.

Dependencies are timestamp extraction from `dbformat.h`, comparator timestamp support, and `InternalIterator`. Risks include non-owned child lifetime, asserts instead of runtime validation for timestamp support, possible infinite loops if a child iterator misbehaves, and partial forwarding because APIs such as `PrepareValue()` and `write_unix_time()` are not overridden. No direct tests are in this subset; relevant signals would seek forward/backward across cutoff boundaries and verify status/pinning forwarding.
