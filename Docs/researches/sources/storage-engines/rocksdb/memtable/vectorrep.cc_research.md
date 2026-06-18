# sources/storage-engines/rocksdb/memtable/vectorrep.cc

## Purpose
`vectorrep.cc` implements a vector-backed `MemTableRep` optimized for buffering writes and sorting lazily at read/iteration time. It is useful for workloads where append cost matters and sorted access can be deferred.

## Important APIs, Types, and Functions
- `VectorRep` implements `Insert`, `InsertConcurrently`, `Contains`, `MarkReadOnly`, `ApproximateMemoryUsage`, `BatchPostProcess`, `Get`, and `GetIterator`.
- `bucket_` is a shared vector of `const char*` memtable keys.
- `tl_writes_` stores per-thread vectors for concurrent insertion buffering.
- `Iterator` owns or shares a bucket snapshot and lazily sorts it with `stl_wrappers::Compare`.

## Control Flow
Single-threaded `Insert()` writes directly into `bucket_` under `rwlock_` and increments `bucket_size_`. `InsertConcurrently()` appends to a thread-local vector. `BatchPostProcess()` drains the calling thread's local vector into the shared bucket under write lock, updates size, deletes the local vector, and resets the thread-local pointer.

Reads take a read lock and either use the immutable shared bucket or copy the mutable bucket into a temporary vector. Iterators sort on first use. `Seek()` performs an `equal_range` binary search for the first entry not less than the encoded target. `Get()` seeks to the lookup memtable key and invokes the callback forward.

## State and Persistence Behavior
State is in memory only. `immutable_` controls whether readers may share and lazily sort the main bucket. `sorted_` records whether the shared immutable bucket has been sorted. Mutable reads copy the vector so they can sort without mutating active writer state.

## Dependencies and Integration Points
The implementation depends on `MemTableRep`, `Arena`, `ThreadLocalPtr`, `port::RWMutex`, `MutexLock`, option metadata, and `stl_wrappers::Compare`. `VectorRepFactory` registers the `count` reserve option and creates the representation.

## Risks and Test Signals
`Contains()` checks pointer equality with `std::find`, not comparator equality, so it only answers whether the exact key pointer exists. `SeekAndValidate()` returns `NotSupported` for non-empty memtables, and `SeekForPrev()` asserts false. Concurrent insertion requires callers to invoke `BatchPostProcess()` to publish thread-local writes. `ApproximateMemoryUsage()` counts vector pointer slots only, not key payload memory. Test signals are mostly generic memtable tests and benchmark behavior.
