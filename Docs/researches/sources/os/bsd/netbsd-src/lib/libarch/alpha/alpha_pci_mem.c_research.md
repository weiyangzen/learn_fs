# File Research: sources/os/bsd/netbsd-src/lib/libarch/alpha/alpha_pci_mem.c

Implements Alpha userland helpers for mapping PCI/EISA/ISA memory space, historically for XFree86.

Key behavior:
- Maintains cached globals `alpha_pci_mem_windows` and `alpha_pci_mem_window_count`.
- `alpha_pci_mem_map` rejects `BUS_SPACE_MAP_LINEAR` without `BUS_SPACE_MAP_PREFETCHABLE`.
- Lazily calls `alpha_bus_getwindows(ALPHA_BUS_TYPE_PCI_MEM, &abw)` and searches a bus window containing the requested address range.
- Requires dense windows for prefetchable mappings and sparse windows for non-prefetchable mappings.
- Opens `_PATH_MEM`, computes shifted sparse/dense offsets, maps physical memory with `mmap(PROT_READ|PROT_WRITE, MAP_FILE|MAP_SHARED)`, then closes the descriptor.
- Copies the chosen `alpha_bus_space_translation` into the caller-provided `rabst` on success.
- `alpha_pci_mem_unmap` calls `munmap` with the size shifted by `abst_addr_shift`.

Dependencies:
- Alpha `sysarch` bus-window API and `machine/sysarch.h`.
- `/dev/mem` via `_PATH_MEM`.
- `bus_addr_t`, `bus_size_t`, `BUS_SPACE_MAP_*`, and `ABST_DENSE`.

Notes and risks:
- Global window cache is unsynchronized.
- Caller must pass the returned translation to unmap with the same sparse/dense size semantics.
- Sparse mapping size expansion can surprise callers that think only in bus bytes.
