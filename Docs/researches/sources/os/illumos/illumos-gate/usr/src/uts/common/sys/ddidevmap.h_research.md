# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ddidevmap.h

This header defines kernel devmap and user-memory mapping implementation types and public devmap-related flags. It includes `sys/mman.h` under `_KERNEL`.

Kernel-private structures include `devmap_info`, `ddi_umem_cookie`, `devmap_callback_ctl`, `devmap_softlock`, `devmap_ctx`, devmap fault/read-write enums, and `devmap_handle_t`. These represent driver mappings into user address spaces, umem-backed mappings, soft locking, CPU-context tracking, and callback operations for map/access/dup/unmap.

`ddi_umem_cookie_t`, `ddi_as_handle_t`, `devmap_pmem_cookie_t`, and `devmap_cookie_t` are opaque or semi-opaque mapping handles. `struct ddi_umem_cookie` records allocation size, virtual address, lock, type, page array, owning process/address space, segment flags, lock count, cleanup callbacks, reference count, unlock-list linkage, and locked-memory resource-control tracking.

Devmap callback versioning is `DEVMAP_OPS_REV`. Driver setup flags include defaults, invalid mapping, allow remap, and use page size. Internal handle flags include setup done, lock initialized, locked, and large-page mapping.

Umem allocation and lock flags include sleep/nosleep, pageable, trash mappings, and read/write expected access for `ddi_umem_lock`. The comments warn that VM read/write meaning can be opposite to I/O `B_READ`/`B_WRITE`.

Research notes:
- This header is closely tied to `segdev`, `segkp`, page locking, HAT attributes, and mmap/devmap callbacks.
- Locking and callback lifetime are sensitive: long-term umem cleanup callbacks can occur after a lock call.
- Public drivers mostly see flags and opaque handles, while the kernel implementation sees full structure layouts.
