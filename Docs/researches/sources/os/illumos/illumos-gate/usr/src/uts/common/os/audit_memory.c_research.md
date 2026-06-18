# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/audit_memory.c

This file contains small memory-management helpers for audit process data and audit path strings. It defines the global `au_pad_cache` kmem cache used for `p_audit_data_t` allocations.

`au_pathhold()` and `au_pathrele()` maintain an atomic reference count on `struct audit_path`; the release path frees the variable-sized allocation when the count reaches zero. `au_pathdup()` creates a resized copy of an existing audit path, optionally adding one path section and/or extra string storage. It preserves section offsets by computing new pointers relative to the copied string base, updates the new end pointer, copies existing strings, and initializes the new reference count and allocation size.

The kmem cache constructor/destructor initialize and destroy the `pad_lock` mutex embedded in `p_audit_data_t`. `au_pad_init()` creates the `"audit_proc"` cache with those callbacks.

The main dependencies are atomic reference operations, kmem variable-size allocation, and the audit path layout where section pointers and string storage are packed into a single allocation. Correctness depends on preserving pointer offsets during duplication and matching `audp_size` on free.
