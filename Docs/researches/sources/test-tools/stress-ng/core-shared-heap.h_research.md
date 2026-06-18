# sources/test-tools/stress-ng/core-shared-heap.h

Purpose: declares the shared heap lifecycle and bump allocation interface.

Important APIs/types/functions: `stress_shared_heap_init(metrics_size)` returns an initialization token/pointer on success. `stress_shared_heap_malloc(size)` allocates from the shared heap. `stress_shared_heap_free()` tears the heap down.

Control flow: no runtime code. The API implies init-before-alloc and whole-heap-free teardown.

State and persistence: allocator state is hidden in `g_shared`; returned allocations remain valid until `stress_shared_heap_free`.

Dependencies/integration: includes `core-setting.h` for common stress-ng types/macros. Used by code that needs process-shared storage for metrics/strings.

Risks: callers cannot free individual allocations and must tolerate NULL on exhaustion.

Test signals: build users should verify all allocation paths happen after shared heap init and before free.
