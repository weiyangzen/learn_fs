# File Research: sources/os/linux/linux/fs/cachefiles/daemon.c

## Purpose
Implements the `/dev/cachefiles` misc-device control interface used by `cachefilesd` to configure, bind, monitor, cull, and unbind a CacheFiles cache.

## Main Elements
- File operations: `cachefiles_daemon_open()`, `cachefiles_daemon_release()`, `cachefiles_daemon_read()`, `cachefiles_daemon_write()`, and `cachefiles_daemon_poll()`.
- Open path: requires `CAP_SYS_ADMIN`, enforces single open with `cachefiles_open`, allocates `struct cachefiles_cache`, initializes lists, locks, xarrays, waitqueue, and default culling thresholds.
- Command dispatch: parses newline-terminated user commands and invokes handlers from `cachefiles_daemon_cmds`.
- Threshold commands: `frun`, `fcull`, `fstop`, `brun`, `bcull`, and `bstop` parse percentage limits and enforce `stop < cull < run < 100`.
- Configuration commands: `dir`, `secctx`, `tag`, `debug`, and `bind`.
- Runtime commands: `cull` and `inuse` act on the caller's current working directory.
- On-demand commands: `copen` and `restore` are included when `CONFIG_CACHEFILES_ONDEMAND` is enabled.
- Unbind/refcount path: `cachefiles_get_unbind_pincount()`, `cachefiles_put_unbind_pincount()`, `cachefiles_flush_reqs()`, and `cachefiles_daemon_unbind()`.

## Dependencies And Integration
Bridges userspace cache manager commands to `cache.c`, `namei.c`, `security.c`, and `ondemand.c`. Uses miscdevice registration from `main.c`, xarrays for on-demand requests, daemon poll wakeups, and CacheFiles credential overrides for VFS operations.

## Risk Notes
The daemon lifetime is guarded by `CACHEFILES_DEAD`, `unbind_pincount`, and request xarray flushing. Memory barriers in `cachefiles_flush_reqs()` pair with on-demand request enqueueing to avoid orphaned requests. Command parsing rejects embedded NULs and overly large writes, but each command handler still depends on strict daemon-side sequencing.
