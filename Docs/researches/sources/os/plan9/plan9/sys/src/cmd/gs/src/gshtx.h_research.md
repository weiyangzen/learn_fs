# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gshtx.h

Public high-level interface for stand-alone halftone/transfer objects.

Provides aliases:
- `gs_ht` to `gs_halftone`
- component, spot, threshold, and multiple halftone aliases
- GC descriptor and member-name aliases

Exports:
- `gs_ht_build`
- `gs_ht_set_spot_comp`
- `gs_ht_set_threshold_comp`
- `gs_ht_set_mask_comp`
- `gs_ht_reference`
- `gs_ht_release`
- `gs_ht_install`
- assignment/reference macros

Documents the two-step construction model: create the overall halftone, then fill each component. It also states that client-provided threshold or mask data is not released by the halftone object.

This header is a convenience API over lower-level `gs_halftone` machinery.
