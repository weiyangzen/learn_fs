# File Research: sources/os/linux/linux-stable/fs/affs/amigaffs.c
- Purpose: Implements AFFS shared on-disk helper operations for directory hash chains, hardlink chains, checksums, protection bits, errors, and names.
- Main functions: `affs_insert_hash`, `affs_remove_hash`, `affs_remove_link`, `affs_empty_dir`, `affs_remove_header`, `affs_checksum_block`, `affs_fix_checksum`, `affs_secs_to_datestamp`, `affs_prot_to_mode`, `affs_mode_to_prot`, `affs_error`, `affs_warning`, `affs_check_name`, `affs_copy_name`.
- Hash behavior: Inserts/removes header blocks in AFFS directory hash chains and updates checksums as links change.
- Link removal: Handles AFFS hardlink chain semantics, including replacing a primary header with link metadata when necessary and fixing dcache references.
- Removal flow: Checks directory emptiness, removes hash entries, updates link counts, frees link blocks, and coordinates link/hash locks.
- Metadata conversion: Converts Amiga protection bits to Linux modes and back; converts Unix seconds to Amiga datestamps.
- Error handling: Logs filesystem errors and remounts read-only when appropriate.
- Risks: Link-chain manipulation is complex and buffer/checksum updates must remain atomic enough with the surrounding inode locks.
