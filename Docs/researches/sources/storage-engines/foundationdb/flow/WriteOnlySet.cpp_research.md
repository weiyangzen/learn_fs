<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/WriteOnlySet.cpp -->
# sources/storage-engines/foundationdb/flow/WriteOnlySet.cpp
- Purpose: Implements and tests a lock-free-ish write-only reference set used when sampling is enabled.
- Important APIs/types/functions: Template methods `WriteOnlySet::insert`, `eraseImpl`, `erase`, `replace`, constructor, `copy`, `WriteOnlyVariable::get/replace`, explicit instantiations for `ActorLineage`, and test `/flow/WriteOnlySet`.
- Control flow: Insert pops a free index, addrefs the object, and stores its pointer. Erase atomically clears an entry or handles a concurrently locked entry by queuing deferred ref cleanup. Replace swaps pointers with refcount handling. Copy scans entries, temporarily marks an entry with a low-bit lock, addrefs it, attempts unlock, returns references, and drains deferred cleanup.
- State and persistence behavior: The set owns an atomic pointer array, a free-index queue, and a deferred free list. Reference counts are manually adjusted. No persistence.
- Dependencies and integration points: Compiled under `ENABLE_SAMPLING`; integrates with `ActorLineage` sampling, Flow `Reference`, atomic queues/lists from the header, and unit tests using real threads.
- Risks: Pointer low-bit locking assumes object pointers are at least 2-byte aligned. Concurrent erase/copy paths are subtle and rely on correct deferred cleanup. Capacity exhaustion logs `NoCapacityInWriteOnlySet` and returns `npos`.
- Test signals: The embedded non-simulation test runs five writer threads plus one copier, checks inserts equal erases, ensures instance count returns to zero, and logs aggregate copy/lock statistics.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/WriteOnlySet.cpp -->
