# File Research: sources/virtualization/libblockdev/src/plugins/fs/common.c

## Role

`common.c` provides shared helper functions for filesystem plugin modules.

## Helpers

`synced_close()` calls `fsync()` then `close()` and returns nonzero if close fails. It is used after probing block devices to flush/close file descriptors.

`get_uuid_label()` uses blkid to probe a device and extract `UUID` and `LABEL`, returning empty strings when values are absent. It opens the device read-only with `O_CLOEXEC`, enables partition probing, performs a blkid probe, and duplicates values into caller-owned strings.

`check_uuid()` validates that a supplied UUID is ASCII and parseable as an RFC-4122 UUID after lowercasing through `uuid_parse()`.

## Dependencies

- GLib for errors and strings.
- blkid for probing.
- POSIX open/close/fsync.
- `uuid.h` for UUID validation.
- libblockdev fs error domain from `fs.h`.

## Notable Risks

- `synced_close()` preserves `fsync()` failure only until a successful close; if `fsync()` fails but `close()` succeeds, it returns the original failure value, but callers in this group ignore it.
- `get_uuid_label()` treats missing UUID/label as empty string, not an error.
