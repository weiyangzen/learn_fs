# sources/storage-engines/rocksdb/table/table_iterator.h

Purpose: provides an `Iterator` wrapper around a heap-allocated `InternalIterator` returned by `TableReader::NewIterator`, intended for raw table iteration through public APIs.

Important APIs/types/functions: `TableIterator` deletes copy operations, supports move construction/assignment, owns `InternalIterator*`, forwards all iterator movement/access/status methods, exposes `operator->` and `get`, and returns `NotSupported` for `GetProperty`.

Control flow: constructor takes an already-valid internal iterator. `reset` deletes any existing iterator before taking a new one; move assignment transfers ownership. All public iterator calls delegate directly to the wrapped internal iterator.

State and persistence behavior: state is a single owning raw pointer. It does not persist data; it controls iterator lifetime and deletion.

Dependencies/integration points: used by `SstFileReader::NewTableIterator` to expose raw table keys as an `Iterator`. Integrates public `rocksdb::Iterator` API with table-internal iteration.

Risks: constructor assumes non-null input; forwarded methods dereference `iter_` without null checks. It is only correct for iterators allocated with the default allocator, not arena placement. `GetProperty` asserts false and is not usable.

Test signals: `SstFileReaderTableIteratorTest` verifies raw iteration exposes all internal entries, supports seek/seek-for-prev where the underlying table iterator does, and differs from DB iterator visibility.
