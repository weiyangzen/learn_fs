# File Research: sources/os/linux/linux/fs/ext4/mmp.c

## Purpose

Implements ext4 Multiple Mount Protection (MMP), which prevents the same filesystem from being mounted read-write by multiple nodes at the same time.

## Checksum Handling

- `ext4_mmp_csum()` computes checksum over the MMP structure up to `mmp_checksum`.
- `ext4_mmp_csum_verify()` validates checksums when metadata checksums are enabled.
- `ext4_mmp_csum_set()` updates checksum before writes.

## MMP Block I/O

`read_mmp_block()`:
- Forces a fresh read by clearing buffer uptodate state.
- Uses priority metadata read.
- Validates magic and checksum.
- Releases the buffer and warns on failure.

`write_mmp_block_thawed()`:
- Updates checksum.
- Submits synchronous prioritized metadata write.
- Waits for completion and returns `-EIO` if write failed.

`write_mmp_block()` wraps writes with superblock freeze protection so kmmpd does not dirty buffers on a frozen filesystem.

## Diagnostic Output

`__dump_mmp_msg()` logs the failure reason plus last update time, node name, and block device name from the MMP block. It is used when another active writer or fsck is detected.

## kmmpd Thread

`kmmpd()` is the background MMP updater.

Behavior:
1. Initializes MMP timestamp, node name, and check interval.
2. Loops until stopped or emergency state.
3. Verifies the MMP feature remains enabled.
4. Increments and writes `mmp_seq`.
5. Sleeps for the update interval.
6. If the elapsed time exceeds the check interval, rereads the MMP block and verifies that sequence and node name still match.
7. Adjusts check interval based on observed write/sleep timing.
8. On clean exit, writes `EXT4_MMP_SEQ_CLEAN`.

If it detects overwritten MMP state, it logs details, aborts the filesystem with `EBUSY`, and waits to be stopped.

## Startup Protection

`ext4_multi_mount_protect()` runs during mount.

Flow:
1. Validates the configured MMP block lies inside the filesystem.
2. Reads and validates the MMP block.
3. Computes a check interval from superblock and on-disk MMP fields.
4. Handles special states:
   - `EXT4_MMP_SEQ_CLEAN`: skip initial wait.
   - `EXT4_MMP_SEQ_FSCK`: fail with `-EBUSY`.
5. If sequence is active, waits and rereads to see whether another node updates it.
6. Writes a new random sequence.
7. Waits again and rereads to ensure the sequence remains unchanged.
8. Stores the MMP buffer in `s_mmp_bh`, records block device name, and starts `kmmpd`.

Failure releases the buffer and returns an error such as `-EINVAL`, `-EFSCORRUPTED`, `-EFSBADCRC`, `-ETIMEDOUT`, `-EBUSY`, or `-ENOMEM`.

## Shutdown

`ext4_stop_mmpd()` stops the updater thread, releases the MMP buffer, and clears `s_mmp_tsk`.

## Concurrency and Safety

- Startup writes use `write_mmp_block_thawed()` because mount/remount already protects against freezing.
- Runtime writes use `write_mmp_block()` with freeze protection.
- MMP read/write uses synchronous prioritized metadata I/O to reduce latency and avoid stale device-cache behavior.
- Random sequence generation uses `get_random_u32_below()` bounded by `EXT4_MMP_SEQ_MAX`.

## Research Notes

This file is small but safety-critical. Its correctness depends on conservative wait intervals, fresh reads, synchronous writes, checksum validation, and aborting promptly if the MMP block no longer matches the local updater’s sequence/node identity.
