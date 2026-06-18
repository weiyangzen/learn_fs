# File Research: sources/os/bsd/freebsd-src/sys/sys/disk.h

## Purpose
Defines generic disk ioctls for geometry, media size, flushing, deletion, identifiers, physical paths, attributes, zoned commands, and kernel dump configuration.

## Main Elements
- Basic ioctls: sector size, media size, firmware sectors/heads, flush, delete.
- Identity/path ioctls: `DIOCGIDENT`, `DIOCGPROVIDERNAME`, `DIOCGPHYSPATH`.
- Optimal I/O layout ioctls: stripe size and stripe offset.
- Generic attribute structure `diocgattr_arg`.
- Zoned disk command ioctl `DIOCZONECMD`.
- Netdump/kernel dump ABI: `diocskerneldump_arg`, sentinel indices for remove/all/dev/append, and `DIOCSKERNELDUMP`/`DIOCGKERNELDUMP`.
- Kernel `disk_err()` declaration.

## Dependencies And Integration
Includes `ioccom`, `kerneldump`, `disk_zone`, socket/network headers for netdump, and is used by GEOM/disk providers and disk utilities.

## Risk Notes
Disk identifiers are documented as optional and not guaranteed unique except under specific physical-storage assumptions. Kernel dump fields include user pointers and encryption/compression metadata requiring careful validation.
