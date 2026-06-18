# File Research: sources/teaching/os161/kern/include/membar.h

Defines memory-barrier API and includes machine-specific implementation.

Barriers:
- `membar_load_load`
- `membar_store_store`
- `membar_store_any`
- `membar_any_store`
- `membar_any_any`

Design:
- Uses the same inline/out-of-line pattern as other OS/161 headers via `MEMBAR_INLINE`.
- Documents intended use for lock-like objects, atomics, lock-free structures, and hardware/device register access.

Relevance:
- The listed SFS/semfs code mostly relies on locks rather than explicit barriers; lower-level spinlocks/device code may use these.
