# sources/test-tools/stress-ng/stress-mmapfixed.c

Purpose: `stress-mmapfixed.c` stresses fixed-address mappings and fixed remaps across a descending address range. It maps small regions with random flags, verifies addresses are unmapped before use, optionally mlocks and NUMA-randomizes pages, and remaps regions to deterministic and random fixed addresses.

Important APIs/types/functions: `mmapfixed_info_t` carries `--mmapfixed-mlock`, `--mmapfixed-numa`, and optional NUMA masks. `stress_mmapfixed_is_mapped_slow` probes a region with chunked `mincore` calls. `stress_mmapfixed_is_mapped` first tries `msync` and falls back to mincore scanning. `stress_mmapfixed_child` performs fixed mapping/remapping.

Control flow: the parent reads options, allocates NUMA masks when requested, reports expected memory use, then runs an oomable child. The child starts at `MMAP_TOP` (`0x80000000` on 32-bit or `0x8000000000000000` otherwise), synchronizes, and loops. It chooses a 1-7 page size, randomizes flags including shared/private, locked, noreserve, populate, and fixed-noreplace when available, skips already mapped or low-memory regions, maps at the target address, applies NUMA/mlock/madvise, tries `mremap` to a nearby XOR-derived address, then attempts additional random fixed remaps while preserving a stored sentinel value. It force-unmaps and shifts the address down until `MMAP_BOTTOM`, then resets.

State and persistence behavior: all state is anonymous memory. NUMA masks are parent-owned and freed after the child. No filesystem state is created. The main safety state is address occupancy checking before fixed mappings.

Dependencies and integration points: the file uses core mmap, madvise, mincore/msync shims, NUMA, OOM, signal exit handler, and `mremap` when available. It registers as `CLASS_VM | CLASS_OS`, `VERIFY_ALWAYS`, with `--mmapfixed-mlock` and `--mmapfixed-numa`.

Risks: fixed mappings can overwrite existing mappings if occupancy detection is wrong or races with other allocations. `mincore`/`msync` detection is heuristic and can treat errors as unmapped. `mremap` fixed moves vary by kernel and address-space constraints. Sentinel verification catches remap data loss, but many failures are expected and skipped.

Test signals: run `stress-ng --mmapfixed 1 --mmapfixed-ops 1 --verify`, repeat with `--mmapfixed-mlock`, and on NUMA systems `--mmapfixed-numa`. A remap sentinel mismatch should fail; ordinary failed fixed mappings should not.
