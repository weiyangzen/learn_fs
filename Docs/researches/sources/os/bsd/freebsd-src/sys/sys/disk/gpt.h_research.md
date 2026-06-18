# File Research: sources/os/bsd/freebsd-src/sys/sys/disk/gpt.h

## Purpose
Defines GPT header/entry structures and a large catalog of known GPT partition type GUID constants.

## Main Elements
- Generic `gpt_uuid` definition unless callers provide `GPT_UUID_TYPE`.
- `struct gpt_hdr` models the EFI GPT header and includes explicit padding to keep `hdr_size`/`offsetof` behavior predictable.
- `GPT_MIN_RESERVED` documents the UEFI-required 16 KiB entry reservation.
- `struct gpt_ent` models 128-byte GPT entries with type GUID, entry GUID, LBA range, attributes, and UTF-16 name.
- Entry attributes include platform-required, bootme, bootonce, and bootfailed.
- GUID constants cover unused, EFI, MBR, FreeBSD variants, Microsoft, Linux, VMware, Apple, NetBSD, DragonFlyBSD, ChromeOS, OpenBSD, Solaris, HiFive, U-Boot env, XBOOTLDR, and BIOS boot.

## Dependencies And Integration
Used by GPT partition readers/writers and GEOM partition code.

## Risk Notes
GPT structure sizes are ABI/on-disk critical. GUID byte order follows GPT/DCE layout and must match parser formatting/conversion code.
