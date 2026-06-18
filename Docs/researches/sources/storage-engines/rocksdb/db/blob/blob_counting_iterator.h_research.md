# sources/storage-engines/rocksdb/db/blob/blob_counting_iterator.h

## Purpose
Wraps an `InternalIterator` to measure blob inflow during compaction by passing each visited key/value to `BlobGarbageMeter`.

## Important APIs and Control Flow
The constructor stores the child iterator and meter, then immediately calls `UpdateAndCountBlobIfNeeded`. All positioning and movement methods delegate to the child and then call the update method. `Valid()` requires both child validity and local `status_.ok()`. Data accessors forward to the child under `Valid()` assertions. `NextAndGetResult`, bounds checks, pinning methods, properties, and delete-range sentinel checks mostly pass through.

## State, Dependencies, and Risks
State is a non-owning child iterator pointer, a non-owning `BlobGarbageMeter*`, and a local status. `UpdateAndCountBlobIfNeeded` copies child status when invalid and otherwise calls `ProcessInFlow(key(), value())`, which can turn the wrapper invalid on corrupt blob indexes. Risks include double-counting if the same entry is revisited by seeks, which is intended for measurement semantics in tests, and relying on child status being OK while valid. `blob_counting_iterator_test.cc` directly covers forward/backward/seek and corruption behavior.
