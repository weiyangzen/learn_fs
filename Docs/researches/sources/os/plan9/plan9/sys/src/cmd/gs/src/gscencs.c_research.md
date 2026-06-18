# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gscencs.c

Implements the compact built-in encoding API over generated tables from `gscedata.c`.

Key contents:
- Includes `memory_.h`, `gscedata.h`, `gscencs.h`, `gserror.h`, and `gserrors.h`.
- Defines `gs_c_min_std_encoding_glyph = gs_min_cid_glyph - 0x10000`.
- Implements:
  - `gs_c_known_encode`
  - `gs_c_decode`
  - `gs_c_glyph_name`
  - `gs_is_c_glyph_name`
  - `gs_c_name_glyph`
- Contains optional `#ifdef TEST` standalone test code.

Behavior:
- `gs_c_known_encode(ch, ei)` validates encoding index and character range, then returns the private glyph code by adding `gs_c_min_std_encoding_glyph` to the encoded table value.
- `gs_c_decode(glyph, ei)` binary-searches the reverse table for a glyph and returns the matching character code or `GS_NO_CHAR`.
- `gs_c_glyph_name(glyph, pstr)` unpacks `N_LEN`/`N_OFFSET`, then points `pstr` directly into `gs_c_known_encoding_chars`.
- `gs_is_c_glyph_name(str, len)` checks whether the pointer lies inside the generated character table; it does not verify the exact length argument.
- `gs_c_name_glyph(str, len)` binary-searches the packed character-name table for a given name and returns the corresponding private glyph code or `gs_no_glyph`.

Important implementation notes:
- Encoding glyph numbers from this API are private and only meant for the paired APIs in this file.
- Reverse lookup assumes reverse tables are sorted by glyph value.
- The optional test uses fixed expected `N(len, offset)` values, so it must be updated if regenerated table layout changes.
