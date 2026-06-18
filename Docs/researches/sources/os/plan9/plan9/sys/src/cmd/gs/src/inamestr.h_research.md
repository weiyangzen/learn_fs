# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/inamestr.h

Name string storage and hashing definitions for Ghostscript’s interned-name system.

Key behavior:
- Includes `inameidx.h`.
- Defines a 256-byte Pearson hash permutation via `NAME_HASH_PERMUTATION_DATA`.
- Provides `NAME_HASH`, which hashes a non-empty byte string with Pearson hashing.
- Defines `name_string_t`, holding chained hash/free-list next index, foreign/static ownership flag, GC mark bit, string size, and byte pointer.
- Adjusts bit-field widths according to `EXTEND_NAMES`.
- Defines `name_string_sub_table_t`, an array of `NT_SUB_SIZE` string records.
- Defines `NT_HASH_SIZE` as `1024 << (EXTEND_NAMES / 2)`.

Research notes:
- `name_string_t.next_index` is used for both hash chains and the free list.
- `max_name_string` shrinks when `EXTEND_NAMES` grows, matching the broader index-space tradeoff described in the other name headers.
