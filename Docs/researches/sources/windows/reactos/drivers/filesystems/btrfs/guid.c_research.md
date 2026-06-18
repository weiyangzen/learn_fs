# File Research: sources/windows/reactos/drivers/filesystems/btrfs/guid.c

## Purpose

`guid.c` is GUID glue for the ReactOS Btrfs filesystem driver.

It includes:
- `<ntifs.h>`
- `<initguid.h>`
- `<ntddstor.h>`

Including `initguid.h` in one translation unit causes GUID definitions from included headers to be emitted rather than only declared.

## Research Notes

The file contains no functions or runtime logic. Its role is build/link support for storage and kernel GUID symbols used elsewhere in the driver.
