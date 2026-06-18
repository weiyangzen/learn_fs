# File Research: sources/os/bsd/openbsd-src/sys/sys/conf.h

This header defines OpenBSD block/character device switch tables, line discipline tables, and device-switch initializer macros.

Key definitions:
- Device classes/flags: `D_DISK`, `D_TTY`, `D_CLONE`.
- Block device switch: `struct bdevsw` with open/close/strategy/ioctl/dump/size/type.
- Character device switch: `struct cdevsw` with open/close/read/write/ioctl/stop/tty/mmap/type/flags/kqfilter.
- Line discipline switch: `struct linesw`.
- Driver declaration/initializer macros: `dev_type_*`, `dev_decl`, `bdev_decl`, `cdev_decl`, `bdev_disk_init`, `cdev_disk_init`, `cdev_tty_init`, and many device-class-specific initializers.

Kernel APIs:
- Device switch globals: `bdevsw[]`, `cdevsw[]`, `linesw[]`, `swdevt[]`, `chrtoblktbl[]`.
- Mapping/helpers: `bdevsw_lookup`, `chrtoblk`, `blktochr`, `iskmemdev`, `iszerodev`, `getnulldev`.
- Declares many built-in cdev/bdev entry points such as `sd`, `cd`, `vnd`, `rd`, `fuse`, `kstat`, `kcov`, and `dt`.

Risk notes:
- Initializer macros encode default unsupported operations as `enodev`, `enxio`, or `nullop`; choosing the wrong macro changes visible device behavior.
- Some macros intentionally map specialized devices through other implementations, such as `fido`/`ujoy` using `uhid` operations.
