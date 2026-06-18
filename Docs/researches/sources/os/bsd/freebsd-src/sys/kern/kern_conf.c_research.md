# File Research: sources/os/bsd/freebsd-src/sys/kern/kern_conf.c

## Purpose
Implements FreeBSD character-device (`struct cdev`) and device-switch (`struct cdevsw`) management: creation, naming, aliases, cloning, destruction, refcounting, devfs integration, and compatibility wrappers for Giant-locked drivers.

## Main Elements
- Device lifetime:
  - `dev_ref()`, `dev_refl()`, `dev_rel()` maintain `si_refcount`.
  - `dev_refthread()`, `devvn_refthread()`, and `dev_relthread()` protect driver entry calls against concurrent destruction through `si_threadcount`.
  - `dev_unlock_and_free()` defers frees that cannot safely happen while `devmtx` is held.
- Default/dead driver operations:
  - `dead_cdevsw` returns `ENXIO`/`ENODEV` for devices removed unexpectedly.
  - Default no-op or unsupported callbacks are installed when drivers leave callbacks null.
- Giant compatibility:
  - `giant_open()`, `giant_read()`, `giant_write()`, `giant_ioctl()`, `giant_strategy()`, `giant_mmap()`, and related wrappers acquire `Giant` around old drivers marked `D_NEEDGIANT`.
  - `prep_cdevsw()` validates `D_VERSION`, installs defaults, and creates the `d_gianttrick` shadow switch.
- Device creation:
  - `prep_devname()` formats and validates devfs paths, rejecting empty names, spaces, quotes, trailing slashes, `.`/`..`, and duplicates.
  - `make_dev_s()`, `make_dev()`, `make_dev_cred()`, `make_dev_credf()`, and `make_dev_p()` allocate and publish named devfs nodes.
  - `make_dev_alias()`, `make_dev_alias_p()`, and `make_dev_physpath_alias()` create aliases and dependency links to parent devices.
- Device destruction:
  - `destroy_devl()` removes devfs entries, recursively destroys children, drains active thread users, drops cdevpriv state, removes from driver lists, and moves still-referenced devices to `dead_cdevsw`.
  - `delist_dev()` removes names early while requiring later `destroy_dev()`.
  - `destroy_dev_sched_cb()` and taskqueue handlers perform asynchronous destruction, using a Giant-specific queue when needed.
  - `destroy_dev_drain()` waits until a `cdevsw` has no devices.
- Clone support:
  - `clone_setup()`, `clone_create()`, and `clone_cleanup()` manage driver-local clone unit allocation and ordered clone lists.
  - `dev_stdclone()` parses conventional stem-plus-unit names.
- Debugging:
  - Optional DDB `show cdev` dumps cdev reference counts, thread counts, flags, private-data state, and driver pointers.

## Dependencies And Integration
Integrates with `devfs_alloc()`, `devfs_create()`, `devfs_destroy()`, `devfs_free()`, `devctl_notify()`, vnode device references, taskqueues, cdevpriv cleanup, `Giant`, `devfs_inos`, and driver-provided `struct cdevsw` callbacks.

## Risk Notes
This file is highly concurrency-sensitive. Correctness depends on `devmtx`, per-cdev `cdp_threadlock`, deferred free ordering, reference count invariants, and not freeing memory while locks with stricter ordering are held. Device-name validation is security-relevant because names are exposed through devfs and devctl events. Destruction must preserve event ordering and drain in-flight driver entry points.
