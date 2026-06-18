# File Research: sources/os/linux/linux/fs/ntfs3/upcase.c

## Role

Provides NTFS name comparison and hashing using the volume `$UpCase` table. This supports NTFS case-insensitive matching and dentry hashing.

## Major Functions

- `upcase_unicode_char()`:
  - Fast-paths ASCII lowercase to uppercase.
  - Uses the loaded NTFS upcase table for other code units.
- `ntfs_cmp_names()`:
  - Compares two little-endian UTF-16 names.
  - Supports case-sensitive first comparison with case-insensitive fallback when `bothcase` is set.
  - Supports fully case-insensitive comparison when requested.
- `ntfs_cmp_names_cpu()`:
  - Same logic, but compares a CPU-endian `cpu_str` against a little-endian `le_str`.
- `ntfs_names_hash()`:
  - Applies upcase conversion before feeding characters into Linux `partial_name_hash()`.

## Important Invariants

- Callers must provide a valid upcase table when case-insensitive behavior is needed.
- `bothcase` preserves deterministic ordering by returning the original case-sensitive difference when names are equal case-insensitively.
- Length difference breaks ties after common-prefix comparison.

## Dependencies

- Uses `ntfs_fs.h` for NTFS string types and declarations.
- Uses Linux name hashing helpers.

## Notes For Future Work

- The function label/comment spells `case_insentive`; harmless but repeated.
- This code works at UTF-16 code-unit level, not full Unicode normalization. That matches NTFS upcase-table behavior.
