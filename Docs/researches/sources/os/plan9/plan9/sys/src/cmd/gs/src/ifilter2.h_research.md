# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/ifilter2.h

Declares Level 2 filter setup helpers.

Key points:
- Exports setup routines from `zfdecode.c`:
  - `zcf_setup` for CCITTFax
  - `zlz_setup` for LZW
  - `zpd_setup` for PNG/TIFF predictor differencing
  - `zpp_setup` for PNG predictor
- `zcf_setup` takes `gs_ref_memory_t *imem`, reflecting VM-aware parameter storage.

Research relevance:
- Small shared interface for Level 2 decode/filter parameter parsing.
