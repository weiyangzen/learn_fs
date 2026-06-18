# sources/test-tools/stress-ng/stress-ptr-chase.c research

Purpose: implements `ptr-chase`, a CPU cache and memory stressor that builds a large randomized graph of pointer pages and repeatedly follows random next pointers.

Important APIs, types, and functions: `stress_ptrs_t` is a 4 KiB node containing an array of pointers; its low pointer bit is reused as a visited marker. `stress_ptr_chase()` owns allocation, graph construction, traversal, verification-like coverage counting, and metrics.

Control flow: the stressor reads `ptr-chase-pages` with maximize/minimize overrides, allocates half the nodes from heap and half from anonymous mmap, builds a pointer index array, then fills every node slot with a random pointer to a different node. After sync, it starts at node zero and repeatedly selects a random slot, marks the pointer's low bit, masks it back to the real address, follows it, and increments bogo ops until stopped. It then scans all nodes to count marked pointers and records percent chased plus nanoseconds per pointer.

State and persistence: all state is transient heap or anonymous mappings. The low-bit marker mutates stored pointers, but the original address is recovered by masking because allocations are aligned.

Dependencies and integration: uses stress-ng mmap population, memory naming, random generators, metrics, and option parsing. It reports memory usage for instance zero and registers under CPU cache, CPU, memory, and search classes.

Risks: the default name says size but option is pages; very large maximize settings can request substantial memory. Correctness relies on pointer alignment leaving bit zero unused. The visited metric is probabilistic, not a full correctness proof.

Test signals: allocation skips, memory usage reporting, percent-pointers-chased metric, nanoseconds-per-pointer metric, and clean heap/mmap release are the observable signals.
