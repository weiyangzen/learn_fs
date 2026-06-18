# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/inamestr.h

Internal name-string representation header for Ghostscript’s name table. It defines the Pearson hash data and the per-name string metadata stored parallel to `name` entries.

Key contents:
- Includes `inameidx.h`.
- Defines `NAME_HASH_PERMUTATION_DATA`, a 256-byte permutation used for Pearson-style string hashing.
- Defines `NAME_HASH`, a macro that computes a rolling hash for non-empty byte strings.
- Defines `name_string_t` with bitfields for `next_index`, `foreign_string`, GC `mark`, and `string_size`.
- Derives `name_extension_bits`, `name_string_size_bits`, and `max_name_string` from `EXTEND_NAMES`.
- Defines `name_next_index` and `set_name_next_index` macros.
- Defines `name_string_sub_table_t`, matching the name subtable size.
- Defines `NT_HASH_SIZE`, scaled by extended-name mode.

Notable dependencies:
- `inameidx.h`.

Research notes:
- `NAME_HASH` assumes `size >= 1`; zero-length name handling is special-cased elsewhere by the initialized name-table entries.
- The same `next_index` field is used for both hash chains and the free-name list.
- Extended-name mode trades maximum string length for a larger name index space by shifting bits from `string_size` into `next_index`.
