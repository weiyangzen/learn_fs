# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/openpromio.h

## Purpose

`openpromio.h` defines the legacy OpenPROM ioctl data structure and ioctl command numbers used to query and manipulate OpenBoot/OpenPROM properties and device-tree paths.

## Data Structure

`struct openpromio` contains `oprom_size` and a union payload used either as a byte array for property names/values or as an integer node/length field. Macros alias the union as `oprom_array`, `oprom_node`, and `oprom_len`.

The header documents a historical `SETOPT` compatibility issue: old driver and eeprom behavior used `strlen()` rather than `oprom_size`, so `OPROMSETOPT2` exists as the working interface for non-ASCII or size-sensitive property values.

`OPROMMAXPARAM` is 32768, four times the largest noted 8K property size.

## Ioctls

Ioctl constants are built from `OIOC`. Commands include get/set/next option, raw config ops for next/child/getprop/nextprop/proplen, console/framebuffer/boot/version queries, path-to-driver and devfs/prom path conversion, deprecated 64-bit readiness, current node setting, snapshot/copyout, ASR key/export operations, and bootpath retrieval.

Console return bits identify keyboard stdin, framebuffer stdout, and OpenPROM support.

## Research Notes

The ABI intentionally uses void-typed ioctls because copy sizes vary and the driver handles copyin/copyout manually. Risk areas are buffer sizing, null termination versus `oprom_size`, and command compatibility with old firmware/userland expectations.
