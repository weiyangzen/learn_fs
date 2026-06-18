# File Research: sources/os/bsd/freebsd-src/sbin/fdisk/fdisk_mbr_enc.h

Header for MBR partition entry encode/decode helpers.

Contents:
- Uses `#pragma once`.
- Forward declares `struct dos_partition`.
- Declares:
  - `dos_partition_dec(void const *pp, struct dos_partition *d)`
  - `dos_partition_enc(void *pp, struct dos_partition *d)`

Role:
- Shared by `fdisk.c` and `fdisk_mbr_enc.c`.
