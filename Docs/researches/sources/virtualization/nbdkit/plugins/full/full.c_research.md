# File Research: sources/virtualization/nbdkit/plugins/full/full.c

This plugin simulates a block device that reads as zeroes but fails all space-consuming writes with `ENOSPC`.

Key behavior:
- Requires `size=<SIZE>` and stores it globally.
- `.pread` zero-fills every read.
- `.pwrite` and `.trim` fail with `errno = ENOSPC`.
- `.extents` reports the entire export as hole plus zero.
- `.can_cache` returns native cache because data is synthetic and already available.
- Multi-connection is safe.

Intentional behavior:
- `.zero` is omitted so nbdkit fast-zero handling returns `ENOTSUP` for fast zeroes, while normal zeroes fall back to `.pwrite` and report `ENOSPC`.
- `.flush` is omitted because successful writes never happen.

Integration:
- API version 2 plugin.
- Uses nbdkit parse helpers and extent API.

Risks:
- Simple global `size`; no per-connection state.
- Mainly useful as a behavior-testing or failure-simulation plugin.
