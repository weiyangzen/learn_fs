# sources/test-tools/stress-ng/core-shared-heap.c

Purpose: provides a primitive shared-memory bump allocator used for data that needs process-shared lifetime without per-object free.

Important APIs/types/functions: `stress_shared_heap_init` maps the heap and creates a process-shared lock. `stress_shared_heap_malloc` allocates aligned chunks by advancing an offset. `stress_shared_heap_free` reports out-of-memory, unmaps the heap, destroys the lock, and clears state.

Control flow: init rounds requested metrics size up to a page, ensures at least one byte before rounding, clears shared-heap flags/list head, maps anonymous shared memory, names it, marks it mergeable, and creates a lock named `shared-heap`. On lock failure it unmaps and returns null. Allocation acquires the lock, checks remaining bytes, sets an out-of-memory flag on failure, aligns size to pointer width when advancing, releases the lock, and returns the previous offset address.

State and persistence: all allocator state lives under `g_shared->shared_heap`: heap pointer, size, offset, lock, list head, and out-of-memory flag. Allocations persist until whole-heap free; there is no individual free.

Dependencies/integration: uses `core-lock`, mmap helpers, madvise mergeable, page-size helper, and `g_shared`. It includes stressor enumeration only to derive maximum stressor context in related shared data.

Risks: no bounds hardening beyond size check; callers must request correct sizes and handle NULL. Offset is not reset in the shown init path except through global initialization assumptions, so repeated init without zeroed `g_shared` would be risky. No per-object destructor exists.

Test signals: initialize with zero and non-page sizes, concurrent allocation under lock, exhaustion flag/reporting, pointer alignment, and free after failed lock creation.
