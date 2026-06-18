# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gzht.h

Declares internal halftone construction, installation, and cache APIs. It covers sampled/threshold/client orders, screen enumeration, halftone cache sizing, fractional color helpers, and colorant-name resolution.

Important elements:
- `gs_screen_enum_s`: holds sampled halftone, order, transform matrices, position, and graphics state.
- `gx_ht_cache_s`: stores cached tiles, backing bits, copied order, cache level geometry, and render callback.
- Cache limits distinguish small and large memory builds.
- `gx_ht_install`, `gx_imager_dev_ht_install`, and transfer reset routines install effective halftones into graphics state/imager state.

This is central to raster output quality and memory use. It is not filesystem code, but it includes architecture-sensitive cache sizing.
