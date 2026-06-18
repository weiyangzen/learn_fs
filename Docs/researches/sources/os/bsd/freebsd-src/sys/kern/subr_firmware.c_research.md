# File Research: sources/os/bsd/freebsd-src/sys/kern/subr_firmware.c

## Purpose
Implements the kernel firmware image registry, firmware lookup/autoloading, direct binary firmware file loading, reference counting, and unload handling.

## Key Elements
- Internal wrapper: `struct priv_fw`.
- Public registry APIs: `firmware_register()`, `firmware_unregister()`, `firmware_get()`, `firmware_get_flags()`, `firmware_put()`.
- Global table: `firmware_table`.
- Synchronization: `firmware_mtx`.
- Taskqueue: `firmware_tq`.
- Autoload task: `loadimage()`.
- Unload task: `unloadentry()`.
- Direct file loader: `try_binary_file()`.
- Loader-preloaded firmware import: `firmware_binary_files()`.
- Module glue: `firmware_modevent()`.

## Behavior
Firmware images are registered by name with data pointer, size, version, and optional parent image. Children hold references on parent images when used. Lookup is case-insensitive and can match absolute firmware paths by trailing component.

If `firmware_get_flags()` cannot find an image, privileged callers at securelevel 0 may trigger module autoload on the firmware taskqueue. If module loading fails, it tries `/boot/firmware/<imagename>` subject to `debug.firmware_max_size`. Successful direct file loads are registered with `FW_BINARY`.

`firmware_put()` decrements references and, when requested with `FIRMWARE_UNLOAD`, schedules unload work for autoloaded images. Binary firmware is freed directly; kld-backed firmware is released through the linker and expected to unregister on module unload.

## Research Notes
Loading is bounced to a taskqueue because linker and vnode I/O need a safe thread context and directory state. The mountroot event sets up taskqueue directory context once root is mounted.
