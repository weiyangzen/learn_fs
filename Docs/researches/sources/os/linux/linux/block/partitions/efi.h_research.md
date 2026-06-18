# File Research: sources/os/linux/linux/block/partitions/efi.h

## Summary
Defines on-disk EFI GPT and protective-MBR structures, GPT constants, and common partition-type GUIDs.

## Main Contents
- Protective MBR constants: `MSDOS_MBR_SIGNATURE`, `EFI_PMBR_OSTYPE_EFI_GPT`.
- GPT constants: header signature, revision, primary header LBA.
- GUID constants for EFI system, legacy MBR, Microsoft reserved/basic data, Linux RAID, Linux swap, and Linux LVM partitions.
- Packed structures: `gpt_header`, `gpt_entry_attributes`, `gpt_entry`, `gpt_mbr_record`, `legacy_mbr`.

## Important Details
All GPT on-disk fields are little-endian and structures are packed. `gpt_entry` includes type GUID, unique partition GUID, start/end LBAs, attributes, and a 72-byte UTF-16LE name field.

## Risks
Consumers must use endian helpers and avoid assuming natural alignment. The header omits the reserved tail of a logical block; readers allocate a full logical block but validate only the header-sized portion.
