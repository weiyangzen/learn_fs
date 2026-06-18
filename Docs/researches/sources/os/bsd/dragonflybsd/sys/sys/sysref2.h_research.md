# File Research: sources/os/bsd/dragonflybsd/sys/sys/sysref2.h

Inline sysref reference-count helpers.

Key contents:
- Kernel-only header.
- Declares slow path `_sysref_put`.
- Defines inline:
  - `sysref_get`
  - `sysref_put`
  - `sysref_isactive`
  - `sysref_isinactive`
  - `sysref_islastdeactivation`
- Declares kernel APIs:
  - `sysref_init`
  - `sysref_alloc`
  - `sysref_activate`

Important behavior:
- `sysref_get` asserts the object is not put away, then atomically increments.
- `sysref_put` fast-paths normal decrements with compare-and-set.
- `sysref_put` falls back to `_sysref_put` for 1-to-0, negative, or racing transitions.
- Negative refcounts mark deletion/deactivation.
- `-0x40000000` identifies the last deactivation reference.

Research notes:
- This is deliberately small and hot-path oriented.
- Correctness depends on callers respecting `SRF_PUTAWAY` and the negative-refcount lifecycle.
