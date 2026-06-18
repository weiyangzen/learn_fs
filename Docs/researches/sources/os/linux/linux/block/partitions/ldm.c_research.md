# File Research: sources/os/linux/linux/block/partitions/ldm.c

## Summary
Implements Windows Logical Disk Manager dynamic disk parsing. It recognizes MBR type `0x42`, validates the LDM database, parses VBLK records, and emits the data partitions that belong to the current disk.

## Main Responsibilities
- Detects candidate dynamic disks from the MBR partition type.
- Validates primary/backup `PRIVHEAD` records.
- Validates TOCBLOCK records and VMDB consistency.
- Reads and parses VBLK disk, disk-group, volume, component, and partition records.
- Reassembles fragmented VBLKs.
- Filters database partitions to the current physical disk GUID.
- Creates Linux partition entries sorted by on-disk start sector.

## Key APIs
- `ldm_partition()`.
- Validation helpers: `ldm_validate_partition_table()`, `ldm_validate_privheads()`, `ldm_validate_tocblocks()`, `ldm_validate_vmdb()`.
- VBLK helpers: `ldm_parse_vblk()`, `ldm_ldmdb_add()`, `ldm_frag_add()`, `ldm_frag_commit()`.
- Output helper: `ldm_create_data_partitions()`.

## Important Behavior
The parser accepts PRIVHEAD version 2.11 and 2.12, checks the database is within disk bounds, ensures logical disk and database regions do not overlap, and compares primary and backup metadata. Vista-style missing TOCBLOCK backups are tolerated as long as at least one valid TOCBLOCK exists and all found copies match.

VBLK fields use variable-width length-prefixed integers and strings. `ldm_relative()` range-checks each variable field offset before the type-specific parser reads it. Partition VBLKs carry start, size, volume offset, parent id, disk id, and optional partition number.

Fragmented VBLKs are grouped by record group id, deduplicated, marked incomplete when broken, and committed only when all fragments are present.

## State and Lifetime
`struct ldmdb` owns parsed global headers plus per-type linked lists of allocated `struct vblk`. All VBLK lists and fragment lists are freed before return.

## Risks
The format has many variable-length and versioned fields; correctness depends on the offset validation in every parser path. The emitted Linux partition numbers are based on discovered partition-object order for the current disk, not necessarily Windows volume numbering.
