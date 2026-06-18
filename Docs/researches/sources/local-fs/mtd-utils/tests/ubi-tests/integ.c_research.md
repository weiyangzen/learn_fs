# File Research: sources/local-fs/mtd-utils/tests/ubi-tests/integ.c

## Role
Randomized UBI integrity stress test. It loads/reloads the UBI module, creates test volumes, performs random writes/erases/verifications on logical eraseblocks, and verifies data survives a UBI module reload.

## Main Behavior
- Maintains in-memory models for UBI devices, volumes, open volume file descriptors, eraseblocks, and write records.
- Creates one dynamic volume per UBI device when needed, using all available bytes or `--maxebs`.
- Writes deterministic pseudo-random data to page-aligned regions and records seed/offset/size for later verification.
- Verifies unwritten gaps contain `0xFF` and written regions match regenerated data.
- Randomly opens/closes volume fds, writes, erases LEBs via `UBI_IOCEBER`, and periodically reloads the UBI module.
- Removes all created volumes at the end.

## Interfaces And Dependencies
- Uses `libubi_open`, `ubi_get_info`, `ubi_get_dev_info1`, `ubi_mkvol`, `ubi_get_vol_info1`, `ubi_rmvol`.
- Uses volume device nodes directly with `open`, `read`, `write`, `lseek`, `dup`, and `close`.
- Depends on test helpers from `common.h` and `helpers.h`, including `seed_random_generator`.

## Notes
- Device-node creation is explicitly marked FIXME and falls back to a shell `mknod` command.
- `open_volume()` returns `0` despite allocating and linking a `struct volume_fd *`; callers ignore the return value.
- Designed for destructive test environments: it rejects pre-existing volumes and removes volumes it creates.
