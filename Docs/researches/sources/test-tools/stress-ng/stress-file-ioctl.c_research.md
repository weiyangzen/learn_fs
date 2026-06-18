# sources/test-tools/stress-ng/stress-file-ioctl.c

Purpose: implements `file-ioctl`, a filesystem ioctl coverage stressor that creates temporary files and exercises generic, clone/dedupe, allocation, mapping, and filesystem-specific ioctl commands.

Important APIs/types/functions: `check_flag()` validates that `FIONBIO` and `FIOASYNC` actually toggle `O_NONBLOCK`/`O_ASYNC` as observed through `F_GETFL`. `stress_file_ioctl_fs_t` maps filesystem names to btrfs, ext, nilfs, reiserfs, and xfs probe functions. The Linux `shim_space_resv` structure backs reservation ioctls not always exposed by libc headers. `stress_file_ioctl()` is the main loop and tracks whether any ioctl was compiled in.

Control flow: the stressor creates and unlinks a 1 MiB temp file, detects filesystem type, optionally creates and unlinks a destination file for reflink/dedupe ioctls, preallocates and syncs the files, synchronizes, then loops over all compiled ioctl blocks. It exercises close-on-exec, nonblocking/async, size and block queries, reflink/range clone, dedupe, invalid fd queries, version/xattr, reserve/unreserve/zero range, FIBMAP, UUID/sysfs path, and filesystem-specific probes, incrementing bogo once per full pass.

State and persistence behavior: uses unlinked temp files held open by fd. No durable file remains after close and temp-dir removal. Some ioctls mutate file allocation and flags during the run.

Dependencies and integration points: uses Linux fs headers when available, stress-ng temp-file helpers, filesystem info helpers, bad-fd helper, fallocate/fsync shims, and metrics-free bogo integration. Registered as `CLASS_FILESYSTEM | CLASS_OS`, `VERIFY_ALWAYS`.

Risks: ioctl availability is highly kernel/filesystem/header dependent; many calls are expected to fail. The ext4 UUID branch contains direct `write(1, "here\n", 5)` and `pr_inf("UUID...")`, which can pollute stdout/log output if compiled and supported. Freeze/thaw ioctls are intentionally disabled as fragile. Some checks validate side effects only when `F_GETFL` is available.

Test signals: run on ext4, xfs, btrfs, and filesystems without clone/dedupe support. Confirm no "no available file ioctls" skip on normal Linux builds, flag toggling checks pass, unsupported ioctls fail quietly, and stdout is inspected if EXT4_IOC_GETFSUUID is enabled.
