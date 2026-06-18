# File Research: sources/os/bsd/openbsd-src/sys/sys/reboot.h

Defines reboot/boot flags and legacy boot-device number encoding helpers.

Key contents:
- Reboot flags for askname, single-user, no sync, halt, default root, kernel debugger, read-only root, dump, miniroot, config, bad time, powerdown, serial console, user request, reset, good random seed, unhibernate, and confidential VM boot.
- Boot-device bit shifts/masks for adaptor, controller, unit, partition, and type.
- `MAKEBOOTDEV()` macro and magic constants.
- Kernel declarations for `reboot()` and `boot()`.

Risk notes:
- Flags are passed through boot/init paths and may be interpreted by machine-dependent code.
