# File Research: sources/os/linux/linux-stable/fs/adfs/map.c
- Purpose: Implements ADFS free-space/fragment map reading, validation, lookup, and statfs accounting.
- Main functions: `lookup_zone`, `scan_free_map`, `scan_map`, `adfs_map_statfs`, `adfs_map_lookup`, `adfs_checkmap`, `adfs_map_read`, `adfs_read_map`, `adfs_free_map`.
- Format model: Treats the map as zones containing variable-sized fragment bitstreams with fragment IDs and free-space records.
- Lookup flow: Converts fragment ID and file offset into a zone/map offset, scans map entries, and returns a physical sector/block address.
- Validation: Recomputes zone check and cross-check bytes before accepting the map.
- Integration: Used by inode block mapping and superblock mount/statfs logic.
- Risks: Bit-level parsing, signed shifts, zone wrapping, and corrupt-map handling are central to safe reads.
