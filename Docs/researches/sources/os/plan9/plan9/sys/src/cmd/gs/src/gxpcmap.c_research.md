# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxpcmap.c

`gxpcmap.c` implements PatternType 1 color mapping, rendered-pattern accumulation, and pattern-cache management.

The file defines default cache sizes, smaller under `arch_small_memory` or debug. It registers GC descriptors for color tiles, tile arrays, pattern cache, and pattern accumulator devices.

Pattern rendering uses `gx_device_pattern_accum`, a forwarding device that optionally owns a color memory device and a mono mask device. `pattern_accum_open` configures dimensions/resolution from the target device, allocates mask when `uses_mask`, and allocates color bits for colored patterns. Drawing procs forward fill/copy operations into the color target and update the mask. Close releases the mask and unretains the accumulator.

`gx_pattern_alloc_cache` creates a direct-mapped tile table. `gx_pattern_cache_add_entry` strips fully opaque masks, computes bitmap memory usage, evicts by id slot and round-robin budget pressure, then stores tile metadata and steals bitmap buffers from accumulator memory devices. `gx_pattern_cache_add_dummy_entry` creates high-level-device placeholder tiles.

`gx_pattern_load` renders the pattern PaintProc into an accumulator, inserts it, then verifies lookup. `gs_pattern1_remap_color` handles null patterns, uncolored pattern base-color remapping, masked device-color type substitution, and cache loading.

Risks are manual bitmap ownership transfer, direct cache collisions, and fatal behavior if accumulator bit readback is requested for uncolored-only paths.
