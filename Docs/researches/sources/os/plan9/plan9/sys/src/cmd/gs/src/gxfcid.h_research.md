# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxfcid.h

Defines CID-keyed font structures.

- Includes CID, base font, and Type 42 font headers.
- Defines common CID data `gs_font_cid_data`:
  - `CIDSystemInfo`
  - `CIDCount`
  - `GDBytes`
- Defines CIDFontType 0 (`gs_font_cid0`):
  - common CID data
  - `CIDMapOffset`
  - `FDArray` of Type 1 subfonts
  - `FDBytes`
  - `glyph_data` callback
  - `proc_data`
- Defines CIDFontType 1 (`gs_font_cid1`), carrying base font data plus `CIDSystemInfo`.
- Defines CIDFontType 2 (`gs_font_cid2`) as a Type 42 subclass:
  - common CID data
  - `MetricsCount`
  - `CIDMap_proc`
  - saved original Type 42 outline/metrics procs for wrappers
- Provides GC descriptors for CID font data and concrete CID font types.
- Declares:
  - `gs_font_cid_system_info`
  - `gs_font_cid0_enumerate_glyph`
  - `gs_is_CIDSystemInfo_compatible`
  - `gs_cid0_indexed_font`
  - `gs_cid0_has_type2`

Role: internal representation for CID fonts and their subfont/mapping relationships.
