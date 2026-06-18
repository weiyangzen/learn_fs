# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/ifilter2.h

Declares Level 2 filter setup helpers.

Key points:
- Exports setup routines from `zfdecode.c`:
  - `zcf_setup` for CCITTFax (`stream_CF_state`)
  - `zlz_setup` for LZW (`stream_LZW_state`)
  - `zpd_setup` for PNG/TIFF predictor diff (`stream_PDiff_state`)
  - `zpp_setup` for PNG predictor (`stream_PNGP_state`)

Dependencies and interactions:
- Used by Level 2 filter operator implementations to parse dictionaries into stream states.
- `zcf_setup` takes `gs_ref_memory_t *imem`, reflecting VM-aware parameter storage.

Research relevance:
- Narrow interface for shared Level 2 decode/filter parameter parsing.
