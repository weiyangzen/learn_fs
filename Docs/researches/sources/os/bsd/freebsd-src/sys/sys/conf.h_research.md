# File Research: sources/os/bsd/freebsd-src/sys/sys/conf.h

## Purpose
Defines FreeBSD character device objects, character device switch ABI, devfs device creation/destruction entry points, clone-device hooks, and kernel dump device plumbing.

## Main Elements
- `struct cdev` describes devfs-visible devices: flags, timestamps, credentials, refs, children/aliases, driver private pointers, switch pointer, I/O sizing, and name.
- Driver callback typedefs cover open, fdopen, close, read, write, ioctl, poll, mmap, strategy, kqueue filter, purge, and mmap-single.
- Device classes and flags: `D_TAPE`, `D_DISK`, `D_TTY`, `D_MEM`, `D_TRACKCLOSE`, `D_MMAP_ANON`, `D_NEEDGIANT`, `D_NEEDMINOR`.
- `struct cdevsw` is the driver operation table with versioning and internal device lists.
- Device registration helpers: `DEV_MODULE*`, `make_dev*`, `make_dev_alias*`, `destroy_dev*`, `dev_ref*`, `dev_rel*`, `dev_depends()`.
- Clone support: `clone_setup()`, `clone_create()`, `clone_cleanup()`, `dev_stdclone()`, `dev_clone` eventhandler.
- Kernel dump support: dumper callback typedefs, `struct dumperinfo`, `dump_savectx()`, dumper insert/remove/create/destroy, and dump write lifecycle functions.

## Dependencies And Integration
Integrates with devfs, vnode device references, kernel modules, eventhandlers, credentials, GEOM/dump code, and the implementation in `sys/kern/kern_conf.c`.

## Risk Notes
This is a core driver ABI. `struct cdevsw` versioning, `struct cdev` lifetime, devfs private data ownership, and kernel dump callback contracts are compatibility- and concurrency-sensitive.
