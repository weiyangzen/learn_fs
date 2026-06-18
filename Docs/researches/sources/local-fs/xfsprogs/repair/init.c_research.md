# File Research: sources/local-fs/xfsprogs/repair/init.c

## Role

`init.c` initializes libxfs and process-level repair prerequisites.

## Main Flow

`xfs_init`:

- Clears and fills a `libxfs_init` descriptor from global command options.
- Configures data, log, and realtime device names.
- Chooses libxfs access flags:
  - read-only/inactive for no-modify,
  - dangerous inactive mode when requested,
  - exclusive mode by default,
  - direct I/O always,
  - buffer locking when prefetch is enabled.
- Falls back to dangerous inactive initialization only to emit a targeted read-only mounted filesystem error.
- Creates thread-specific keys for data and attr block maps.
- Raises file-size rlimit to infinity.
- Initializes prefetch tracing.
- Runs CRC32C and directory/attribute hash self-tests before examining the filesystem.

## Support Helpers

- `ts_create`: creates pthread keys for per-thread block-map caching.
- `increase_rlimit`: ensures repair can write large outputs/metadata without `RLIMIT_FSIZE` interference.

## Interactions

This file must run before phase processing because later code assumes libxfs devices, buffer cache behavior, thread-local block maps, and hash/CRC primitives are ready.
