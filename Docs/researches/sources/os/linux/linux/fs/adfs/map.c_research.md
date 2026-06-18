# File Research: sources/os/linux/linux/fs/adfs/map.c

Implements ADFS free-space/object map parsing, validation, lookup, and statfs accounting.

Key behavior:
- Describes the ADFS map as zones containing variable-length fragment bitstreams.
- `lookup_zone()` scans a zone for a fragment id and resolves an offset within repeated fragments.
- `scan_free_map()` follows free-fragment links and sums free map bits.
- `scan_map()` searches starting from the fragment’s expected zone and wraps across zones if needed.
- `adfs_map_statfs()` computes total blocks, files, free blocks, and available blocks from map data.
- `adfs_map_lookup()` maps a fragment id plus object offset to a physical sector/block:
  - Root fragment starts at the middle zone.
  - Other fragments start at `frag_id / ids_per_zone`.
  - Converts between sector offsets and map-bit offsets using `s_map2blk`.
- Computes and validates zone checksums and map crosscheck byte.
- Lays out zone metadata, including first-zone disk-record area and last-zone truncation to filesystem size.
- Reads all map zones from disk.
- `adfs_read_map()` initializes map geometry from the disk record, reads map blocks, validates them, and returns an allocated `adfs_discmap`.
- `adfs_free_map()` releases buffer heads and frees the map array.

Important interactions:
- All ADFS file and directory block mapping depends on `adfs_map_lookup()`.
- Mount fails if map validation fails.
