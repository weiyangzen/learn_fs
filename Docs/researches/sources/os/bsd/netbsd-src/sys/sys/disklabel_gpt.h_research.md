# File Research: sources/os/bsd/netbsd-src/sys/sys/disklabel_gpt.h

Defines EFI GUID Partition Table header, entry structures, attributes, and known partition type GUID constants.

Key content:
- `struct gpt_hdr` matching GPT header fields.
- GPT signature, revision, primary header block number, header size.
- `struct gpt_ent` with type GUID, unique GUID, start/end LBA, attributes, UCS-2 name.
- Attributes for required partition, no block I/O protocol, legacy BIOS bootable, and FreeBSD boot flags.
- GUID constants for EFI, MBR, NetBSD swap/FFS/LFS/RAID/CCD/CGD, FreeBSD types, OpenBSD data, Microsoft reserved/basic/recovery/LDM, Linux data/RAID/swap/LVM/xbootldr, Apple HFS/UFS, BIOS boot, VMware, and SiFive BBL.

Important behavior:
- Notes all GPT fields are little-endian per EFI specification.
- Header is pure structure/constant ABI, with no functions.
