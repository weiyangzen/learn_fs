# File Research: sources/os/bsd/dragonflybsd/sys/sys/flame_graph.h

`flame_graph.h` defines data structures for per-CPU flame graph sampling. It sets the base symbol name `_flame_graph_ary`, frame depth to 32, and default entry count to 256.

`struct flame_graph_entry` stores an array of instruction-pointer-sized return addresses. `struct flame_graph_pcpu` stores entry count, write index, a pointer to entry storage, and padding/dummy fields, cache-aligned.

This header is data-layout only; sampling and export logic live elsewhere.
