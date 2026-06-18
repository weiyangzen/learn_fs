# File Research: sources/os/bsd/netbsd-src/sys/sys/conf.h

Defines core block/character device switch interfaces, line discipline tables, and device major/minor conversion helpers.

Key content:
- Device flag classes: `D_TAPE`, `D_DISK`, `D_TTY`, `D_MPSAFE`, `D_NEGOFFSAFE`.
- `struct bdevsw` and `struct cdevsw` operation vectors.
- Kernel helpers to attach/detach and look up device switches.
- Typedefs and macros for driver operation signatures.
- Default no-op/error operation aliases such as `noopen`, `nullopen`, `nommap`, `nokqfilter`.
- Block and character wrapper declarations: `bdev_open`, `cdev_read`, etc.
- `struct linesw` and line discipline registration/lookup APIs.
- `/dev/mem`, `/dev/null`, `/dev/zero`, `/dev/full` minor constants.
- `struct devsw_conv` for dev node metadata and conversion tables.
- Root/swap configuration declarations.

Important behavior:
- Forms a major part of the kernel device-driver ABI.
- Pulls in `device_if.h`, `queue.h`, and `types.h`.
