# File Research: sources/os/bsd/freebsd-src/sys/sys/smr_types.h

Typed accessor macros for SMR-protected pointers.

Key responsibilities:
- Defines `SMR_POINTER(type)` wrapper to discourage direct pointer access.
- Provides entered-reader load: `smr_entered_load()`.
- Provides serialized writer/reader access: `smr_serialized_load()`, `smr_serialized_store()`, and `smr_serialized_swap()`.
- Provides unserialized load/store helpers for destructor or externally guaranteed safe contexts.
- Provides `smr_kvm_load()` for libkvm access outside the kernel.

Important patterns:
- Every accessor accepts an assertion expression describing the required synchronization.
- In INVARIANTS kernels, these assertions help catch misuse of SMR-protected pointers.
- Stores use release semantics so initialized contents are visible before readers can follow the pointer.
- Swap includes an explicit release fence for concurrent writer cases.

Research relevance:
- Complements `smr.h` by enforcing safer access patterns at pointer field boundaries.
