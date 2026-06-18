# sources/test-tools/fio/lib/axmap.h

Purpose: declares the opaque hierarchical bitmap API used to set, query, reset, and find free numeric slots.

Important APIs/types: opaque `struct axmap`, allocator/free pair, `axmap_set`, `axmap_set_nr`, `axmap_isset`, `axmap_next_free`, and `axmap_reset`.

Control flow/state: callers create a bounded map for values `0..nr_bits-1`, then mutate it through set calls and query availability. `axmap_set_nr` reports how many contiguous bits were newly set, which lets callers deal with already-used ranges.

Dependencies/integration: includes `inttypes.h` and fio bool definitions from `types.h`. The implementation relies on arch bit width and internal bit helpers, but users see only the opaque handle.

Risks/test signals: callers must free the map and must not share it concurrently without external synchronization. Tests should verify that the header contract matches implementation behavior at empty, full, reset, and boundary states.
