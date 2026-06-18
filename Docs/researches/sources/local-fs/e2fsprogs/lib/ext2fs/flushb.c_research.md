# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/flushb.c

## Role

Provides `ext2fs_sync_device()`, a portable helper to fsync a file/device and optionally flush kernel buffer cache state.

## Main Flow

- Calls `fsync(fd)` when available.
- If requested, tries Linux `BLKFLSBUF` first.
- Also tries `FDFLUSH` for floppy devices when defined.
- Returns the first ioctl/fsync errno if flushing fails.

## Dependencies

Uses platform headers for ioctl definitions and supplies Linux fallback constants when missing.

## Risks / Notes

- Buffer-cache flush behavior is platform-specific and may be unsupported.
- `fsync` is unconditional when compiled in, even if `flushb` is false.
