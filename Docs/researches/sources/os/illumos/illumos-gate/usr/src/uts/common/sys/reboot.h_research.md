# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/reboot.h

## Role

`reboot.h` defines boot/reboot flags, the userland `reboot()` prototype, and kernel boot-flag globals/helpers.

## Flags

`RB_AUTOBOOT` is zero. Other flags control boot behavior:
- ask boot name, single-user, no sync, halt.
- alternate init name, skip boot rc.
- debugger/debug boot behavior.
- crash dump.
- writable root.
- boot argument string.
- config/reconfigure/verbose modes.
- forthdebug and kmdb loading.
- boot-cluster suppression.
- debugger entry at boot.

## Kernel Interfaces

Outside assembly, userland gets `int reboot(int, char *)`.

Under `_KERNEL`, the header declares `boothowto`. For boot code, `bootflags()` takes a string buffer and size; otherwise it takes `struct bootops *`.

## Research Notes

This header is a stable boot-control ABI. Numeric flag values are externally meaningful to boot loaders, init, kernel reboot paths, and debugging tools.
