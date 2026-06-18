# File Research: sources/os/bsd/dragonflybsd/sys/sys/gpt.h

`gpt.h` defines GUID Partition Table on-disk structures and partition type UUID constants. It includes `sys/uuid.h`.

`struct gpt_hdr` models the GPT header, including signature, revision, size, CRCs, self/alternate LBAs, usable range, disk UUID, partition table location, entry count/size, and table CRC. It explicitly pads the structure and asserts the minimum header size when `CTASSERT` is available. `struct gpt_ent` models a 128-byte partition entry with type UUID, unique UUID, LBA range, attributes, and UTF-16 name.

The header defines standard EFI/MBR entries plus DragonFly, FreeBSD, Microsoft, Linux, VMware, Apple, NetBSD, ChromeOS, OpenBSD, BIOS boot, and PReP boot type GUIDs.
