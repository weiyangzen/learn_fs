# File Research: sources/os/bsd/netbsd-src/lib/libc/include/isc/heap.h

ISC heap interface.

Defines:
- Callback types for priority comparison, index updates, and iteration.
- `struct heap_context` fields for array size, increment, heap size, heap array, and callbacks.
- Private-symbol remaps for heap operations.

APIs: `heap_new`, `heap_free`, `heap_insert`, `heap_delete`, `heap_increased`, `heap_decreased`, `heap_element`, `heap_for_each`.
