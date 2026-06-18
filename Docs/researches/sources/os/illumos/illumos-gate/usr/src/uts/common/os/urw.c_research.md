# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/urw.c

Implements safe kernel reads and writes of another process's user address space through `uread()` and `uwrite()`.

Key responsibilities:
- Validates whether a target user page is meaningful and backed by real data.
- Temporarily adjusts protections when necessary.
- Soft-locks the target page, maps it into kernel virtual address space, copies data, and soft-unlocks it.
- Handles ordinary memory pages, device mappings, ISM shared segments, `MAP_NORESERVE` segvn pages, and `/dev/null` style segdev mappings.

Important paths:
- `page_valid()` rejects file mappings beyond EOF, addresses outside real ISM shared segment size, `/dev/null` segdev mappings, and unmaterialized `MAP_NORESERVE` anonymous pages.
- `mapin()` uses `hat_getpfnum()` and `ppmapin()` for normal memory pages with page structures; otherwise it allocates heap virtual space and maps device PFNs with `hat_devload()`.
- `urw()` locks the address space as writer, finds the segment, optionally expands protection with `SEGOP_SETPROT()`, soft-faults the page with `F_SOFTLOCK`, copies under `on_trap(OT_DATA_EC)`, syncs I-cache for executable writes, soft-unlocks, restores protection, and drops the address-space lock.
- `uread()` and `uwrite()` are thin wrappers selecting read or write mode.

Locking and fault behavior:
- Uses `AS_LOCK_ENTER(as, RW_WRITER)` to stabilize mappings and avoid copy-on-write races during read softlocks.
- Uses `S_READ_NOCOW` for segvn reads so soft-locking does not unnecessarily break sharing.
- Converts corrupt-memory traps to `EIO` and unmapped/invalid cases to `ENXIO`.

Filesystem relevance:
- It validates vnode-backed mappings against file size and VOP attributes, so it is relevant to `/proc`, debugging, and core/memory inspection paths that read or modify process memory mapped from files or devices.
