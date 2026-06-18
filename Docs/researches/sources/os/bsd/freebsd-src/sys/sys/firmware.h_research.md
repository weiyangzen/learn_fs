# File Research: sources/os/bsd/freebsd-src/sys/sys/firmware.h

## Purpose
Declares the kernel loadable firmware registry abstraction.

## Main Interfaces
- `struct firmware`: name, data pointer, data size, version.
- Registration:
  - `firmware_register`
  - `firmware_unregister`
- Lookup:
  - `firmware_get`
  - `firmware_get_flags`
  - flag `FIRMWARE_GET_NOWARN`
- Release:
  - `firmware_put`
  - flag `FIRMWARE_UNLOAD`

## Dependencies And Integration
Firmware images are often embedded in kernel modules. The registry tracks references so modules containing firmware data cannot unload while in use. Dependent images may reference a master image.

## Risk Notes
Clients must pair `firmware_get*` with `firmware_put`. Automatic module loading depends on master image name matching the module name.
