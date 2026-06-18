# File Research: sources/windows/reactos/ntoskrnl/io/iomgr/ramdisk.c

## Role

`ramdisk.c` contains boot-time RAM disk startup support. It finds a loader-provided XIP ROM memory descriptor, asks the RAM disk driver to create a boot disk, creates ARC and drive-letter symbolic links, initializes `NtSystemRoot`, and waits for PnP enumeration.

## Main entry point and behavior

- `IopStartRamdisk()` scans `LoaderBlock->MemoryDescriptorListHead` for a `LoaderXIPRom` descriptor. Missing data causes `RAMDISK_BOOT_INITIALIZATION_FAILED` with `RD_NO_XIPROM_DESCRIPTOR` (lines 23-78).
- It populates `RAMDISK_CREATE_INPUT` for a fixed `RAMDISK_BOOT_DISK`, using descriptor base page and page count, `RAMDISK_BOOTDISK_GUID`, and a hardcoded drive letter `C` (lines 80-92).
- Loader command-line options are uppercased in place and parsed for `RDIMAGEOFFSET` and `RDIMAGELENGTH`, adjusting disk offset and length (lines 94-146).
- It opens `\Device\Ramdisk`, sends `FSCTL_CREATE_RAM_DISK`, and bugchecks if the driver open or IOCTL fails (lines 148-203).
- It converts the disk GUID to a string, builds a `\Device\Ramdisk{guid}` target, and creates `\ArcName\ramdisk(0)` as a symbolic link to it (lines 205-248).
- A ReactOS-specific block creates an `X:` drive-letter symlink to the RAM disk device and writes `SharedUserData->NtSystemRoot` as `X:` plus the loader boot path (lines 250-275).
- It waits on `PiEnumerationFinished` before returning success (lines 277-287).

## Dependencies and side effects

The function depends on the loader memory descriptor format, the RAM disk device and FSCTL contract from `ntddrdsk.h`, object-manager symbolic links, and the PnP enumeration event exported as `PiEnumerationFinished`.

## Implementation gaps and risks

- Failure paths are hard bugchecks because this is boot-critical code.
- Command-line parsing mutates `LoaderBlock->LoadOptions` with `_strupr()` and uses simple `strstr()`/`atol()` parsing without validating numeric bounds or underflow when subtracting the offset from disk length (lines 96-143).
- The drive-letter handling is explicitly called a ReactOS hack; it hardcodes `X:` and bypasses mount manager policy (lines 250-275).
