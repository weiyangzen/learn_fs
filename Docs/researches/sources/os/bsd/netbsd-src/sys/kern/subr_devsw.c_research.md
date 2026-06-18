# File Research: sources/os/bsd/netbsd-src/sys/kern/subr_devsw.c

## Summary
Implements block and character device switch registration, lookup, name/major conversion, dynamic table expansion, detach synchronization, and wrapper methods for driver operations.

## Main Responsibilities
- Initializes `device_lock` and detach condition variable.
- Attaches block/character driver switch entries by name and major number.
- Dynamically expands `bdevsw`, `cdevsw`, and conversion tables up to `MAXDEVSW`.
- Detaches devsw entries after preventing new references and draining local references.
- Converts between names, block majors, char majors, block `dev_t`, and char `dev_t`.
- Wraps block operations: open, cancel, close, strategy, ioctl, dump, flags/type, size, discard, detached.
- Wraps character operations: open, cancel, close, read, write, ioctl, stop, tty, poll, mmap, kqfilter, discard, flags/type, detached.
- Emits SDT probes for device operation entry/return and open acquire/release events.

## Important Behavior
Dynamic attach allocates reference tables and expanded switch arrays only once, publishing them with atomic stores so readers can safely use either old or new arrays. `*_lookup_acquire()` uses pserialize and optional `localcount` references so detach can wait for in-flight opens.

`devsw_detach_locked()` verifies no autoconf device instances remain for associated drivers, clears switch entries, uses `xc_barrier()` to wait for lockless lookups to observe the removal, and drains localcounts before freeing them.

Open wrappers acquire a referenced autoconf device instance when `d_devtounit` is provided, stabilizing `device_lookup()` during driver `d_open`. Non-MPSAFE drivers are serialized with the kernel lock.

## Dependencies
Uses generated static `bdevsw0`/`cdevsw0`/`devsw_conv0` tables, `localcount`, `pserialize`, `xc_barrier`, autoconf `device_lookup_acquire()`, `config_detach_commit()`, SDT probes, and kernel locking.

## Risks
Detach safety depends on callers ensuring no open instances remain and future opens fail. Many non-open wrappers still use simple lookup without acquired localcount, matching the file's own note that opened vnode references should eventually make those checks unnecessary.
