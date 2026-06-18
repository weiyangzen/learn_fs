# File Research: sources/os/linux/linux-stable/fs/cachefiles/daemon.c

This file implements the `/dev/cachefiles` daemon control interface. It provides a single-open misc-device protocol used by cachefilesd or equivalent userspace to configure, bind, monitor, cull, and optionally operate on-demand cache requests.

Major elements:
- `cachefiles_daemon_fops`: file operations for open, release, read, write, poll, and llseek.
- `cachefiles_daemon_cmds`: command table mapping text commands to handlers: `bind`, `brun`, `bcull`, `bstop`, `cull`, `debug`, `dir`, `frun`, `fcull`, `fstop`, `inuse`, `secctx`, `tag`, plus `copen` and `restore` when on-demand mode is enabled.
- `cachefiles_daemon_open()`: requires `CAP_SYS_ADMIN`, enforces single open with `cachefiles_open`, allocates and initializes `struct cachefiles_cache`, default thresholds, xarrays, lists, waitqueue, and unbind refcount.
- `cachefiles_daemon_release()`: marks the cache dead, flushes on-demand requests if enabled, detaches the file from the cache, and drops the unbind pin.
- `cachefiles_daemon_read()`: returns either ordinary culling/threshold state or delegates to on-demand request reads.
- `cachefiles_daemon_write()`: copies and parses one command string, serializes command execution with `daemon_mutex`, and dispatches to the matching handler.
- `cachefiles_daemon_poll()`: exposes readable state changes, on-demand requests, and culling state.

Configuration command behavior:
- `dir`: sets the cache root path once.
- `tag`: sets an FS-Cache cache tag once.
- `secctx`: converts a security context to a secid once.
- `frun/fcull/fstop` and `brun/bcull/bstop`: set percentage thresholds with strict ordering `stop < cull < run < 100`.
- `bind`: validates thresholds, requires `dir`, optionally enables on-demand mode, defaults tag to `CacheFiles`, and calls `cachefiles_add_cache()`.
- `cull` and `inuse`: operate relative to the daemon process current working directory and reject names containing `/`.

Concurrency and lifetime:
- `unbind_pincount` protects delayed unbind while anonymous on-demand fds may still exist.
- `cachefiles_flush_reqs()` completes and erases all pending on-demand requests, using a memory barrier paired with enqueue-side checks to avoid orphaned requests during teardown.
- `daemon_mutex` prevents overlapping command mutation of cache state.

Security:
- Opening requires admin capability.
- Filesystem operations are performed under cache credentials where appropriate.
- `secctx` is mediated through LSM security conversion.
