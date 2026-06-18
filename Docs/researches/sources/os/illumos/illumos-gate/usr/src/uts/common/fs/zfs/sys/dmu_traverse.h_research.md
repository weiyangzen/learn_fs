# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/dmu_traverse.h

Read status: complete, 78 lines.

Purpose: block tree traversal interface for datasets, destroyed datasets, and pools.

Key definitions and APIs:
- `blkptr_cb_t` callback receives SPA, ZIL, block pointer, bookmark, containing dnode physical pointer, and caller argument.
- Traversal flags include pre/post visiting, metadata/data prefetch, hard traversal, and no-decrypt traversal.
- `TRAVERSE_VISIT_NO_CHILDREN` is a special callback return value to skip children.
- APIs: `traverse_dataset()`, `traverse_dataset_resume()`, `traverse_dataset_destroyed()`, `traverse_pool()`.

Important implementation constraints:
- `TRAVERSE_NO_DECRYPT` allows callers to receive raw encrypted dnodes instead of logical decrypted data, because encrypted dnode blocks have encrypted bonus buffers but unencrypted structural fields.

Dependencies: ZFS context, SPA, ZIO, dataset/dnode/ZIL/ARC forward declarations.

Research notes:
- Used by send, scrub, space accounting, deadlist processing, and diagnostic traversal paths.
