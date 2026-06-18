# File Research: sources/virtualization/nvme-cli/libnvme/src/nvme/ioctl.c

Tiny fallback/default implementation for passthrough submission hooks.

Contents:
- `__libnvme_submit_entry()` returns `NULL`.
- `__libnvme_submit_exit()` is a no-op.
- `__libnvme_decide_retry()` returns `false`.

Research notes:
- These are default hook implementations used when callers do not install custom tracing/retry callbacks on a transport handle.
- The retry default is conservative: no retries unless a caller or transport installs a policy.
