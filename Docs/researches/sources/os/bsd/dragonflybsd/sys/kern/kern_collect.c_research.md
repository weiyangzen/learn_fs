# File Research: sources/os/bsd/dragonflybsd/sys/kern/kern_collect.c

## Summary
Implements the `kcollect` rolling statistics framework. A kernel thread samples registered counters every 10 seconds and exposes scale, identifier, and sample records through `kern.collect_data`.

## Main Responsibilities
- Registers and unregisters collection slots with callbacks and scale metadata.
- Provides `kcollect_setvalue` and `kcollect_setscale` for callbacks/rollups.
- Allocates a ring buffer sized by `kern.collect_samples`.
- Runs `kcollect_thread` to populate timestamped samples.
- Exposes collected data through a sysctl.

## Important Behavior
If `kern.collect_samples` is left at `-1`, it auto-sizes to 1024 or 8192 samples based on `kmem_lim_size()`. Each sample stores current `ticks`, realtime, and all callback values. The sysctl emits a scale record, an 8-byte-per-slot id record, then recent samples in reverse chronological ring order.

## Risks
Callbacks run under `kcollect_lock`, so registered callbacks should avoid long blocking behavior. `kcollect_setvalue` assumes the array and sample count are valid and is intended for normal callback-time rollup use.
