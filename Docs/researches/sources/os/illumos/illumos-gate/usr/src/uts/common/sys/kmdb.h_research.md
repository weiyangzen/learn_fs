# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kmdb.h

## Purpose
Defines control constants and kernel-control entry points for loading, unloading, and activating the kernel debugger `kmdb`.

## Main Interfaces
- Ioctl constants:
  - `KMDB_IOC`
  - `KMDB_IOC_START`
  - `KMDB_IOC_STOP`
- Activation flags:
  - `KMDB_F_AUTO_ENTRY`
  - `KMDB_F_TRAP_NOSWITCH`
  - `KMDB_F_DRV_DEBUG`
- Kernel control functions:
  - `kctl_attach()`
  - `kctl_detach()`
  - `kctl_get_state()`
  - `kctl_modload_activate()`
  - `kctl_deactivate()`
- `kctl_boot_activate_f`: boot-time activation callback type.

## Dependencies And Relationships
Includes `sys/modctl.h` and forward-declares `struct bootops`. Used by kmdb control-device and boot/module activation paths.

## Research Notes
The public surface is intentionally small: it is a control-plane header for debugger lifecycle transitions, not the debugger implementation itself.
