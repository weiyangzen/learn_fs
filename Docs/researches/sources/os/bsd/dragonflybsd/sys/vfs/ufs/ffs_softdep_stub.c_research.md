# File Research: sources/os/bsd/dragonflybsd/sys/vfs/ufs/ffs_softdep_stub.c

Compile-time stub implementation used when `SOFTUPDATES` is not configured. It preserves the softdep API surface while making accidental use of softdep-only mutation hooks fail loudly.

Key responsibilities:
- Provides no-op initialization, mount, mount-device fsync, and metadata-sync functions when soft updates are disabled.
- Defines all setup/change/free softdep hooks with `__dead2` panics, preventing code paths from silently relying on missing dependency tracking.
- Keeps the same exported function names as the real softdep implementation, allowing the rest of UFS/FFS to link in non-softdep kernels.

Dependencies:
- Includes `opt_ffs.h` and is compiled only under `#ifndef SOFTUPDATES`.
- Uses local UFS/FFS headers for matching prototypes and type visibility: `quota.h`, `inode.h`, `ffs_extern.h`, and `ufs_extern.h`.

Notable risks:
- Any runtime call to a setup hook in a kernel built without `SOFTUPDATES` panics, so all call sites must be correctly guarded by mount flags or build configuration.
- `softdep_mount()` and `softdep_sync_metadata()` return success without doing work, matching the expectation that no softdep dependencies exist in this build.
