# File Research: sources/os/linux/linux-stable/fs/ext4/mmp.c

## Purpose

Implements ext4 Multiple Mount Protection (MMP). MMP uses a dedicated on-disk block containing a sequence number, timestamp, node name, device name, check interval, and checksum to detect whether a filesystem is already active elsewhere before allowing mount, then maintains that block periodically while mounted.

## Main Responsibilities

- Compute, verify, and set MMP block checksums when metadata checksums are enabled.
- Read the MMP block directly from disk and validate magic/checksum.
- Write MMP updates synchronously with metadata-priority I/O.
- Start and stop the `kmmpd` kernel thread that refreshes MMP sequence/time fields.
- Detect competing mounts or fsck activity during mount-time MMP checks.
- Record diagnostic information about the last updater on MMP failure.

## Key Operations

- `ext4_mmp_csum()`, `ext4_mmp_csum_verify()`, and `ext4_mmp_csum_set()` cover MMP checksum handling using the filesystem checksum seed.
- `write_mmp_block_thawed()` writes the MMP buffer with `REQ_SYNC | REQ_META | REQ_PRIO` and waits for completion.
- `write_mmp_block()` wraps writes with superblock write-freeze protection so a frozen filesystem does not gain dirty buffers.
- `read_mmp_block()` forces a fresh read by clearing buffer uptodate state, uses priority metadata read I/O, checks `EXT4_MMP_MAGIC`, verifies checksum, and reports warnings on failure.
- `__dump_mmp_msg()` logs last update time, node name, and block-device name from an MMP block.
- `kmmpd()` periodically increments and writes the MMP sequence, updates time/node/check interval, throttles write-error reporting, verifies the on-disk block if scheduling delays exceed the check interval, reports suspected multiple mounts, and writes `EXT4_MMP_SEQ_CLEAN` on clean shutdown.
- `ext4_stop_mmpd()` stops the thread and releases the saved MMP buffer.
- `mmp_new_seq()` chooses a random sequence below or equal to `EXT4_MMP_SEQ_MAX`.
- `ext4_multi_mount_protect()` validates the configured MMP block, reads existing state, waits and rereads if the filesystem was not clean, rejects `EXT4_MMP_SEQ_FSCK`, writes a new random sequence, waits again, verifies no other node changed it, stores device name, and starts `kmmpd`.

## Dependencies

- Includes kernel filesystem, random, buffer-head, UTS namespace, and kthread APIs plus `ext4.h`.
- Depends on ext4 metadata checksum helpers, superblock feature/state fields, warning/error reporting, buffer-head I/O submission, scheduler timeouts, freeze protection, and block-device formatting.

## Important Invariants

- The MMP block must lie between `s_first_data_block` and the filesystem block count.
- Mount proceeds only if the sequence is clean or remains unchanged across the required wait/check cycle after writing a new sequence.
- `EXT4_MMP_SEQ_FSCK` is treated as active filesystem checking and causes mount failure with `-EBUSY`.
- `kmmpd` must keep updating the MMP block while mounted; if it observes a different sequence or node after an excessive delay, it treats the filesystem as multiply mounted and aborts.
- Clean unmount attempts to write `EXT4_MMP_SEQ_CLEAN`.

## Research Notes

MMP is intentionally conservative and time-based. It relies on direct, synchronous metadata-priority reads and writes plus a wait/recheck protocol to distinguish stale state from another active node. The code also handles operational diagnostics carefully by preserving and printing the previous updater's timestamp, node name, and device name.
