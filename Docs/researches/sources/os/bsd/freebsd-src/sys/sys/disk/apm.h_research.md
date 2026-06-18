# File Research: sources/os/bsd/freebsd-src/sys/sys/disk/apm.h

## Purpose
Defines Apple Partition Map on-disk structures and known partition type strings.

## Main Elements
- `struct apm_ddr` driver descriptor record with signature, block size, and block count.
- `struct apm_ent` partition map entry with signature, map block count, start, size, name, and type.
- Constants for APM signatures and name/type field lengths.
- Partition type strings for self/free, FreeBSD variants, Apple boot/HFS/UFS.

## Dependencies And Integration
Includes `sys/types.h`; consumed by partition parsing and GEOM partition code.

## Risk Notes
Fields model an on-disk big-endian historical format. Parsers must handle byte order and fixed-size non-NUL-padded strings correctly.
