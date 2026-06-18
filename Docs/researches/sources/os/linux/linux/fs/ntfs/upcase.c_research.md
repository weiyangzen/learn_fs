# File Research: sources/os/linux/linux/fs/ntfs/upcase.c

Read coverage: complete file, 70 lines.

This file generates the legacy NTFS driver's default Unicode upcase table.

Key logic:
- `generate_default_upcase()` allocates `default_upcase_len` little-endian UTF-16 entries with `kvcalloc()`.
- Initializes identity mapping for all entries.
- Applies three compact tables:
  - range/add mappings for broad lowercase-to-uppercase spans,
  - duplicate alternating pairs where odd entries map to previous entries,
  - explicit word mappings for individual code points.
- Returns the generated table or `NULL` on allocation failure.

Integration:
- Called by `super.c` to create a global default upcase table under `ntfs_lock`.
- Volume `$UpCase` tables are compared with this generated table and may share it by reference.

Risk:
- The table is fixed and partial to NTFS expectations; correctness depends on matching Windows/NTFS upcase semantics used by on-disk indexes.
