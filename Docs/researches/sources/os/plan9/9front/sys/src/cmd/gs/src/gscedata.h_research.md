# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gscedata.h

## Role

`gscedata.h` declares the generated built-in encoding data used by `gscencs.c`.

This is font encoding infrastructure, not filesystem code.

## Encoding Packed-Value Macros

- `NUM_LEN_BITS` is 5.
- `N(len, offset)` packs length and offset into one integer.
- `N_LEN(e)` extracts the length.
- `N_OFFSET(e)` extracts the offset.

## Exported Data

- `gs_c_known_encoding_chars[]`
- `gs_c_known_encoding_total_chars`
- `gs_c_known_encoding_max_length`
- `gs_c_known_encoding_offsets[]`
- `gs_c_known_encoding_count`
- `gs_c_known_encodings[]`
- `gs_c_known_encodings_reverse[]`
- `gs_c_known_encoding_lengths[]`
- `gs_c_known_encoding_reverse_lengths[]`

## Generation Notes

Header comments identify `toolbin/encs2c.ps` as the generator and list the source encoding files. The header must remain consistent with both generated `gscedata.c` and consumer `gscencs.c`.

## Dependencies

- Requires `ushort` to be visible to includers, usually through Ghostscript base type headers.

## Notable Risks

- If `NUM_LEN_BITS` changes, all generated `N(...)` values and consumers must change together.
