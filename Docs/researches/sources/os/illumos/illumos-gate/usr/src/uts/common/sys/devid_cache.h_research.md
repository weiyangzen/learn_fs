# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/devid_cache.h

This private kernel header defines the devid cache nvlist identifiers, in-memory cache records, tunables, and debug logging macros.

The persistent `/etc/devices/devid_cache` top-level nvpair identifier is `DP_DEVID_ID`. Kernel record `nvp_devid` stores a list node, device id, registered path, devinfo pointer, and flags. Flags distinguish registered entries and entries with a current dip.

Tunables control boot/postboot devid discovery, always-discover behavior, discovery interval, and cache read/write disable flags. `devid_report_error` enables more verbose error reporting even in non-debug kernels.

Under `DEBUG`, logging macros gate registration, find, lookup, match, path, error, discovery, hold, unregister, remove, stale, and detach messages. Helpers print debug path and devid information. Non-debug builds compile these away except `DEVIDERR`, which remains controlled by `devid_report_error`.

Research notes:
- This header supports the private devid persistence machinery declared in `ddi_implfuncs.h`.
- Cache entries bridge persistent device IDs, paths, and live devinfo nodes.
- Logging knobs are intentionally granular because devid discovery can be noisy.
