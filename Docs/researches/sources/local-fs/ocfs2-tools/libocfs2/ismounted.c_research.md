# File Research: sources/local-fs/ocfs2-tools/libocfs2/ismounted.c

Checks whether a device or file is mounted, swap-backed, root-mounted, read-only, or busy.

Main APIs:
- `ocfs2_check_mount_point(device, mount_flags, mtpt, mtlen)` fills OCFS2 mount flags and optional mountpoint text.
- `ocfs2_check_if_mounted(file, mount_flags)` is a wrapper without mountpoint output.

Mount detection:
- With `mntent`, `check_mntent_file()` scans `/proc/mounts` on Linux, then the system mtab path. It compares both path strings and stat-derived device identities.
- It validates mtab entries by statting mount directories and checking mounted device identity to avoid stale entries.
- It has special handling for root filesystem detection, including a write probe to `/.ismount-test-file` to detect read-only root when mtab may be unreliable.
- With `getmntinfo`, a BSD-style fallback compares device names under `_PATH_DEV`.

Swap and busy detection:
- `is_swap_device()` scans `/proc/swaps`, comparing path and block-device `st_rdev`.
- Linux block devices are opened with `O_RDONLY | O_EXCL`; `EBUSY` adds `OCFS2_MF_BUSY`.

Flags produced:
- `OCFS2_MF_MOUNTED`
- `OCFS2_MF_ISROOT`
- `OCFS2_MF_READONLY`
- `OCFS2_MF_SWAP`
- `OCFS2_MF_BUSY`

Notable implementation details:
- Derived from e2fsprogs mount checking and modified for OCFS2.
- Some paths use `strncpy(mtpt, ..., mtlen)` without explicitly forcing NUL termination if the mountpoint is longer than the buffer.
- If `mtpt` is NULL, callers must still ensure paths that write mountpoint text are not reached with a NULL buffer in swap handling; current `ocfs2_check_if_mounted()` passes NULL and `is_swap_device()` path calls `strncpy(mtpt, "<swap>", mtlen)`, which is a latent NULL dereference if used on a swap device with that wrapper.
