# File Research: sources/local-fs/xfsdump/inventory/inv_fstab.c

Manages the inventory fstab, the top-level table mapping filesystem UUIDs to mount points and device paths.

Key functions:
- `fstab_getall()` opens `INV_FSTAB`, reads the counter and all `invt_fstab_t` entries, and leaves the file locked exclusive for the caller.
- `fstab_put_entry()` creates the fstab if missing, initializes counters, avoids duplicate UUID entries, and appends a new filesystem entry.
- `fstab_get_fname()` resolves an inventory filesystem prefix path from UUID, mount point, or device path.
- `fstab_DEBUG_print()` prints mount, device, and filesystem UUID entries.

Important dependencies:
- Feeds `init_idb()` and any code needing a filesystem-specific `.InvIndex` path.
- Uses `INV_DIRPATH/<uuid>` plus `.InvIndex` naming convention.

Notable observations:
- Duplicate detection is UUID-only; commented code suggests mount/device matching was once considered.
- `fstab_getall()` locks exclusive even for read-only access, so callers must unlock/close.
- Some error paths in `fstab_get_fname()` can return without freeing `arr` when no UUID is found.
