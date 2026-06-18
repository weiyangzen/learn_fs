# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsstype.h

Defines the core structure descriptor types used by Ghostscript's allocator and garbage collector.

Key definitions:
- Opaque `gc_state_t`.
- `enum_ptr_t`, the return carrier for enumerated object or string pointers.
- Proc signatures for clear-marks, enumerate-pointers, relocate-pointers, and finalize callbacks.
- `gs_memory_struct_type_s`, containing object size, structure name, optional shared procs, per-type callbacks, and callback data.
- `extern_st(st)` macro for structure descriptor declarations.

Research notes:
- Comments constrain finalizers: they must not allocate or resize allocator-managed objects and cannot assume referenced managed objects still exist.
- `EV_CONST` preserves historical enum callback constness while minimizing compiler warnings.
