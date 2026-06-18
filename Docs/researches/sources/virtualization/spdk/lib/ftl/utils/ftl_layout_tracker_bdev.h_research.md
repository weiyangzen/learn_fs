# File Research: sources/virtualization/spdk/lib/ftl/utils/ftl_layout_tracker_bdev.h

Public API for bdev layout tracker.

Defines region properties:
- Type.
- Version.
- Block offset.
- Block size.

Exposes init/fini, add, remove, find-next, blob store/load, and exact insert. Used by NVC/base metadata layout management and superblock v5 blob storage.
