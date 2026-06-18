# sources/storage-engines/leveldb/include/leveldb/iterator.h

Purpose: declares the common iterator interface for DBs, tables, internal merged iterators, and error/empty iterators.

Important APIs and types: abstract `Iterator`, `Valid`, `SeekToFirst`, `SeekToLast`, `Seek`, `Next`, `Prev`, `key`, `value`, `status`, `RegisterCleanup`, `CleanupNode`, `NewEmptyIterator`, and `NewErrorIterator`.

Control flow: callers seek before reading, move forward/backward while valid, inspect key/value slices until the next iterator mutation, then check `status`. Cleanup callbacks run when the iterator is destroyed.

State and persistence behavior: no persistence itself. Iterators often pin resources such as versions, cache handles, table blocks, or snapshots through cleanup callbacks.

Dependencies and integration: table cache registers cache-handle release cleanups; DB and table APIs return `Iterator*`. Uses `Slice` and `Status`.

Risks and edge cases: non-const iterator methods need external synchronization if shared across threads. `key()` and `value()` slices have limited lifetime. Cleanup callbacks must tolerate destruction order.

Test signals: issue 200 covers direction switching behavior at the DB iterator layer; table and DB tests exercise iterator contracts broadly.
