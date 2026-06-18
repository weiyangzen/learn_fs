# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/mem.h

Purpose: Defines memory device minor numbers, private `/dev/mem` ioctls, FMA memory retirement ioctls, and kernel helpers/logging structures.

Key definitions:
- Minor numbers: `/dev/mem`, `/dev/kmem`, `/dev/null`, `/dev/allkmem`, `/dev/zero`, `/dev/full`.
- `MEM_VTOP` ioctl and `mem_vtop_t`/`mem_vtop32_t` for virtual-to-physical translation.
- Private FMD ioctls: naming/info, page retire/unretire/isretired/error queries, retire causes, serial ID.
- Page error bits and `MEM_FMRI_MAX_BUFSIZE`.
- `mem_name_t` and `mem_info_t` for memory FRU/naming and topology data.

Kernel-only:
- `impl_obmem_pfnum()`
- `plat_mem_do_mmio()`
- `mm_logentry_t` for logging writes to memory devices.

Important detail: Several interfaces are explicitly private to FMD/libkvm and not stable application/driver contracts.

Relevance to subset A: Core memory/device ABI, relevant to OS kernel behavior.
