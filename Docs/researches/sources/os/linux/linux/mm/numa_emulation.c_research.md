# File Research: sources/os/linux/linux/mm/numa_emulation.c

## Role

Boot-time NUMA emulation support. It rewrites a parsed physical NUMA memory layout into fake NUMA nodes according to `numa=fake` command-line settings, rebuilds CPU-to-node and distance mappings, and provides CPU mask update helpers that account for emulated-to-physical node relationships.

## Key Behavior

- Stores the `numa=fake` command line through `numa_emu_cmdline()` and maintains `emu_nid_to_phys[MAX_NUMNODES]`, mapping each emulated node id back to its physical node id.
- `mem_hole_size()` uses absent PFNs to discount holes when calculating usable memory spans.
- `emu_setup_memblk()` appends a fake memory block to the emulated meminfo, assigns the emulated nid, records the physical backing nid, advances or removes the consumed physical block, and logs the fake node range.
- `split_nodes_interleave()` divides RAM into a requested number of fake nodes interleaved across parsed physical nodes. It accounts for holes, enforces a minimum fake-node size, gives some nodes an extra 32 MiB to absorb remainders, and adjusts around DMA32 and end-of-node boundaries to avoid unusably small remaining chunks.
- `split_nodes_size_interleave_uniform()` supports both fixed-size fake nodes and uniform per-physical-node splits. Uniform mode divides physical capacity without hole accounting; non-uniform fixed-size mode treats the requested size as a minimum amount of non-reserved memory and expands ranges across holes.
- `split_nodes_size_interleave()` is the fixed-size wrapper used for `numa=fake=<size>M/G`.
- `numa_emulation()` is the coordinator. If no command-line emulation is requested, it restores physical `numa_nodes_parsed` and initializes identity `emu_nid_to_phys`. Otherwise, it copies physical meminfo, parses the command-line mode (`U` uniform, `M/G` fixed size, or plain node count), builds emulated meminfo, validates it through `numa_cleanup_meminfo()`, copies the physical distance table, remaps ACPI PXM/node maps with `fix_pxm_node_maps()`, commits the fake meminfo, and calls `numa_emu_update_cpu_to_node()`.
- Rebuilds NUMA distances for fake nodes. Explicit distances may be parsed after a colon in the fake command line; otherwise distances are inherited from the physical nodes backing each emulated node, with local/remote defaults when physical distances are unavailable.
- Frees the temporary copied physical distance table after successful transformation.
- `numa_add_cpu()` and `numa_remove_cpu()` update each online emulated node's CPU mask for CPUs whose physical node matches the fake node's backing node. With `CONFIG_DEBUG_PER_CPU_MAPS`, updates go through debug cpumask helpers.

## Dependencies

Uses `numa_meminfo`/`numa_memblk` helpers, `numa_nodes_parsed`, memblock allocation/free, absent-page accounting, max PFN state, ACPI NUMA node/PXM map fixups, architecture hooks (`numa_emu_dma_end`, `numa_emu_update_cpu_to_node`, `early_cpu_to_node`), node masks, CPU masks, and NUMA distance APIs.

## Research Notes

This is an early-boot topology transformer. It mutates the same meminfo later registered by `numa_memblks_init()`, so failures deliberately fall back to the original physical topology. The subtle parts are range splitting around holes and DMA32 boundaries, preserving a valid emulated-to-physical mapping for future CPU hotplug, and rebuilding distance tables without losing physical topology information.
