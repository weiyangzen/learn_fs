# File Research: sources/local-fs/kdave-linux/fs/btrfs/scrub.h

Read completely: 22 lines.

This header declares the Btrfs scrub public interface used by the rest of the filesystem. It is guarded by `BTRFS_SCRUB_H`, includes `<linux/types.h>`, forward-declares `struct btrfs_fs_info`, `struct btrfs_device`, and `struct btrfs_scrub_progress`, and exposes only the scrub control/progress functions implemented in `scrub.c`.

The primary entry point is `btrfs_scrub_dev()`. It takes filesystem info, device id, physical start/end range, optional progress output, readonly mode, and a flag indicating whether the run is part of device replace. The function performs the actual scrub/device-replace scan for one device.

The remaining declarations are control-plane helpers: `btrfs_scrub_pause()` requests that running scrubs pause, `btrfs_scrub_continue()` resumes them, `btrfs_scrub_cancel()` cancels all active scrubs for a filesystem, `btrfs_scrub_cancel_dev()` cancels scrub on one device, and `btrfs_scrub_progress()` copies current progress for a device or reports that none is running.

This header deliberately hides all implementation structures such as `scrub_ctx` and `scrub_stripe`. Callers interact through filesystem/device identities and `btrfs_scrub_progress`, keeping scrub internals private to `scrub.c`.
