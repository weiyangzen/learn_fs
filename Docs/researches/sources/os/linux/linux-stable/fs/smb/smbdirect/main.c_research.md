# File Research: sources/os/linux/linux-stable/fs/smb/smbdirect/main.c

## Purpose
SMBDirect module initialization and teardown.

## Initialization
- Defines global `smbdirect_globals` with initialized mutex.
- `smbdirect_module_init()` allocates subsystem workqueues:
  - `smbdirect-accept`
  - `smbdirect-connect`
  - `smbdirect-idle`
  - `smbdirect-refill`
  - `smbdirect-immediate`
  - `smbdirect-cleanup`
- Workqueues use `WQ_SYSFS`, `WQ_PERCPU`, `WQ_POWER_EFFICIENT`; refill/immediate/cleanup are high priority, and cleanup has `WQ_MEM_RECLAIM`.
- Calls `smbdirect_devices_init()` after workqueues are ready.
- On failure, unwinds already allocated workqueues in reverse order.

## Teardown
- `smbdirect_module_exit()` unregisters/cleans devices and destroys all workqueues under the global mutex.

## Module Metadata
- `module_init()` / `module_exit()`
- Description: `smbdirect subsystem`
- License: GPL
