# sources/distributed-fs/tahoe-lafs/src/allmydata/util/gcutil.py

## Purpose

This module helps account for resources that the Python garbage collector cannot directly see, especially bare file descriptors. It triggers full garbage collection after enough unbalanced allocations so descriptor finalizers have a chance to run.

## APIs and control flow

`_ResourceTracker` tracks `_counter` and `_threshold`. `allocate()` increments the counter and calls `gc.collect()` once the threshold is exceeded, then resets the counter. `release()` decrements the counter without allowing it to go below zero. The public singleton is `fileDescriptorResource`, exported through `__all__`.

## State, dependencies, risks, and tests

State is only the tracker counter and threshold. Dependencies are `gc` and attrs. Integration appears in `iputil.CleanupEndpoint`, which allocates duplicated file descriptors and releases them if the endpoint is garbage-collected without being listened on.

Risks include threshold tuning, over-collection cost, missed releases making GC more frequent, and under-accounting if callers allocate descriptors without using the tracker. Test signals should cover counter increment/decrement, threshold-triggered `gc.collect`, reset behavior, no negative counter, and integration with endpoint descriptor cleanup.
