# File Research: sources/os/plan9/9front/sys/src/9/xen/xen-public/io/blkif.h

Imported Xen public block frontend/backend protocol ABI.

Purpose:
- Defines the Xen split block-device protocol, including xenstore negotiation keys, state-machine documentation, request/response opcodes, scatter/gather segment layout, and ring type generation.

Key content:
- Documents notification hold-off using generic ring `req_event`/`rsp_event`.
- Defines `blkif_vdev_t` and `blkif_sector_t`.
- Thoroughly documents backend and frontend xenstore nodes: mode, params, type, barrier/flush/discard/persistent features, ring sizes, sector sizes, sectors, ring refs, protocol, and virtual device properties.
- Documents startup XenBus state transitions.
- Defines request opcodes for read, write, write barrier, flush disk cache, reserved command, and discard/secure discard.
- Defines `BLKIF_MAX_SEGMENTS_PER_REQUEST` as 11.
- Defines `struct blkif_request_segment`, `struct blkif_request`, `struct blkif_request_discard`, and `struct blkif_response`.
- Defines response statuses and `DEFINE_RING_TYPES(blkif, ...)`.
- Defines virtual disk flags for CD-ROM, removable, and readonly.

Integration:
- Directly used by 9front’s Xen block driver `sdxen.c`.
- Combines with `ring.h`, `grant_table.h`, xenstore keys, and event channels for virtual disk I/O.
- This is one of the most relevant files in the group for filesystem/block-storage research.

Risks/notes:
- Sector fields are in 512-byte units even when physical sector size differs.
- Grant references and ring producer/consumer ordering must be managed correctly.
- Feature negotiation is xenstore-string based; missing or stale keys can reduce functionality or break attach.
