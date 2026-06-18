# File Research: sources/os/linux/linux/fs/proc/kcore.c

## Scope

This file implements `/proc/kcore`, an ELF core-file view of kernel virtual memory. It builds ELF headers, notes, and load segments from the current kcore list, RAM map, vmalloc area, optional module range, optional kernel text segment, and vmemmap metadata.

## Public And Internal APIs Covered

- Memory classification callbacks: `register_mem_pfn_is_ram()`, `pfn_is_ram()`.
- Kcore range registration: `kclist_add()`.
- RAM list refresh: `kcore_update_ram()`.
- Read path: `read_kcore_iter()`.
- File ops: `kcore_proc_ops`.
- Memory hotplug notifier: `kcore_callback()`.
- Init: `proc_kcore_init()`.

## Control Flow And Behavior

- Kcore state is held in `kclist_head`, protected by `kclist_lock`, with cached program-header, note, and data offsets.
- `update_kcore_size()` computes one PT_NOTE plus one PT_LOAD per registered kcore range, calculates note size, aligns data start, and updates the proc entry size.
- `kcore_ram_list()` has separate HIGHMEM and non-HIGHMEM implementations. Non-HIGHMEM walks system RAM ranges, converts PFNs to kernel virtual addresses, trims invalid or overflowing ranges, and optionally adds sparsemem vmemmap ranges.
- `kcore_update_ram()` rebuilds RAM and VMEMMAP entries when `kcore_need_update` is set, swaps them into the global list, updates size, and frees stale entries.
- `read_kcore_iter()` emits the ELF file header, program headers, note segment, then segment data. It zero-fills holes and inaccessible pages rather than failing the whole read.
- Data reads handle multiple segment types: vmalloc via `vread_iter()`, user mappings via direct copy, RAM via physical translation and nofault bounce buffer, vmemmap/text via nofault bounce buffer, and unknown types by warning once and zeroing.
- Page offline state is frozen during the read and periodically thawed/rescheduled to avoid racing drivers that mark pages offline.
- `open_kcore()` requires `CAP_SYS_RAWIO`, honors kernel lockdown `LOCKDOWN_KCORE`, allocates a page bounce buffer, refreshes RAM mapping if needed, and syncs inode size.
- Init creates `/proc/kcore` mode `0400`, registers vmalloc, optional text and module ranges, performs the initial RAM update, and registers a memory hotplug notifier.

## Dependencies

- Depends on ELF core structures, vmcoreinfo, memory hotplug, memblock/system RAM walkers, vmalloc, highmem, page offline, hwpoison, lockdown security, capability checks, and architecture hooks for address translation.
- Uses proc permanent read-iter file ops.

## Risks And Invariants

- `/proc/kcore` exposes raw kernel memory and is gated by capability and lockdown checks.
- Reads must tolerate sparse, offline, hwpoisoned, unaccepted, and architecture-unmapped memory by zero-filling.
- The kcore list and computed file size must stay consistent under `kclist_lock`.
- Hotplug only marks the list dirty; actual rebuild happens lazily on open/read setup.
