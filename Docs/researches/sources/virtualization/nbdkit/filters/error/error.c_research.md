# File Research: sources/virtualization/nbdkit/filters/error/error.c

Purpose: randomly injects configured errno failures into selected request types.

Key details:
- Per-operation settings cover `pread`, `pwrite`, `trim`, `zero`, `extents`, and `cache`.
- Error names supported include `EPERM`, `EIO`, `ENOMEM`, `EINVAL`, `ENOSPC`, and `ESHUTDOWN`.
- Supports global and per-operation error code, probability, and trigger-file configuration.
- Trigger files are resolved with `nbdkit_absolute_path`.
- Random state is initialized at load time and protected by a mutex.
- `random_error` skips when rate is zero, checks trigger file if configured, handles 100% rates directly, and uses 32-bit random comparison for partial rates.
- Each wrapped operation either injects `-1` with configured errno or delegates to `next`.

Integration notes:
- Useful for resilience testing of clients and upper filters under controlled operation-specific failures.
