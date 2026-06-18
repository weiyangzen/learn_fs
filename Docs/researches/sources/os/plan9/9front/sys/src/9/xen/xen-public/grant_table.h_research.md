# File Research: sources/os/plan9/9front/sys/src/9/xen/xen-public/grant_table.h

Imported Xen public grant-table ABI.

Purpose:
- Defines Xen’s capability mechanism for sharing pages between domains and transferring page ownership, including grant table entries, operations, flags, handles, and status codes.

Key content:
- Documents grant tables as the memory-sharing foundation for split block and network drivers.
- Defines `grant_ref_t`, grant entry v1, reserved console/xenstore entries, grant types, permit-access flags, transfer flags, and v2 grant entries/status for newer interface versions.
- Defines grant-table hypercall operations: map, unmap, setup, dump, transfer, copy, query size, unmap-and-replace, set/get version, status frames, swap refs.
- Defines map/unmap/setup/transfer/copy/query/version/status structures and guest handles.
- Defines `GNTMAP_*` flags and grant status codes/messages.
- Documents concurrency rules for publishing, invalidating, and modifying grant entries.

Integration:
- Directly used by 9front’s `xengrant.c` to set up one grant-table frame and allocate/release grant references.
- Used by `sdxen.c` for block I/O buffers and by `etherxen.c` for network buffers through `blkif.h`/`netif.h`.
- Included by many I/O protocol headers.

Risks/notes:
- High-risk ABI area: incorrect memory barriers, stale grants, or releasing in-use grants can corrupt cross-domain I/O.
- 9front’s implementation currently maps one grant table frame; expansion requires matching mapping changes.
