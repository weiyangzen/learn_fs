# sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_RGW/up.c

This file implements the RGW FSAL upcall bridge. It receives invalidation notifications from librgw and forwards them into Ganesha's FSAL upcall vector so cached objects can be invalidated.

The only function is `rgw_fs_invalidate(void *handle, struct rgw_fh_hk fh_hk)`. The `handle` argument is expected to be a `struct rgw_export *` that was registered in `main.c` via `rgw_register_invalidate`. The function validates the export and `export->export.up_ops`, wraps the RGW file-handle key in a `gsh_buffdesc`, and calls `up_ops->invalidate(..., FSAL_UP_INVALIDATE_CACHE)`. Errors are logged but not returned because the librgw callback is asynchronous and has `void` return type.

State behavior is transient. The upcall does not persist anything; it translates an RGW handle key into a cache invalidation request. The file relies on the same `struct rgw_fh_hk` layout used by `handle_to_wire` and `handle_to_key`, so cache identity must remain consistent across librgw, Ganesha wire handles, and upcall invalidation.

Dependencies include FSAL APIs, export context headers, common FSAL support, and the RGW internal definitions. The integration point is the callback registration in `create_export`.

Risks include lost invalidations if the export pointer or upcall vector is missing, no retry on `invalidate` failure, and possible cache-key mismatch if librgw changes `fh_hk`. Test signals should include forced invalidation callbacks with valid and null exports, validation that the same key invalidates handles created by lookup/open, and log/error behavior when the upcall vector rejects invalidation.
