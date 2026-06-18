# File Research: sources/os/linux/linux/mm/percpu-stats.c

Debugfs statistics exporter for the dynamic per-CPU allocator.

Key responsibilities:
- Defines global `pcpu_stats` and saved allocation-info snapshot storage.
- Creates `debugfs/percpu_stats` at late init.
- Prints allocator configuration, global allocation/chunk statistics, and per-chunk fragmentation state.
- Scans all chunk lists and the reserved chunk under `pcpu_lock`.
- Computes per-chunk allocation sizes and free fragments from allocation and boundary bitmaps.
- Reports chunk role labels such as first chunk, reserved chunk, sidelined chunk, and to-depopulate chunk.

Important behavior:
- The output buffer for chunk analysis is sized from the maximum live `nr_alloc` across chunks, then revalidated under lock; if too small, it retries.
- Fragment sizes are stored as negative values and allocation sizes as positive values so sorting separates free fragments before allocations.
- Fragmentation is measured only from the beginning of a chunk to the last allocation.
- Statistics are in bytes unless the printed name indicates otherwise.

Dependencies:
- Uses debugfs, seq_file, sort, vmalloc/vfree, percpu internal chunk structures, allocation maps, boundary maps, global chunk lists, and `pcpu_lock`.

Notable risks:
- The debugfs read can be relatively expensive because it scans every chunk while holding the percpu allocator lock during reporting.
- The bitmap-derived fragmentation view depends on allocation/boundary map consistency maintained by the allocator core.
