# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/finddev.c

## Role

Searches common device directories to find a block device pathname matching a `dev_t`.

## Main Flow

- Starts breadth-first search at `/dev`, `/devfs`, and `/devices`.
- `scan_dir()` stats directory entries, queues subdirectories, and checks disk-device `st_rdev` values against the target.
- Search depth is capped by `EXT2FS_MAX_NESTED_LINKS`.
- Returns a newly allocated path string on success or `NULL` on failure.

## Dependencies

Uses POSIX directory/stat APIs and `ext2fsP_is_disk_device()` for device type detection.

## Risks / Notes

- Uses a fixed 1024-byte stack path buffer and skips longer paths.
- Ignores `scan_dir()` errors during top-level traversal except allocation failure that sets no surfaced error in the public API.
- Traversal can be expensive on systems with large `/dev`-like trees.
