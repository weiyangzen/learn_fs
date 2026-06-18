# File Research: sources/os/bsd/freebsd-src/sys/sys/diskmbr.h

## Purpose
Provides the historical MBR write ioctl definition.

## Main Elements
- Includes MBR layout definitions and ioctl helpers.
- Defines `DIOCSMBR` as an ioctl writing a 512-byte MBR buffer.

## Dependencies And Integration
Used by disk management tools/drivers that update MBR contents.

## Risk Notes
Writing raw MBR data is destructive if misused. Kernel handlers must enforce permissions and device safety policy.
