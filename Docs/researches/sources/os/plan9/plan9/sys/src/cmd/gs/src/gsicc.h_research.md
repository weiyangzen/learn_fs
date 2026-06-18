# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsicc.h

Declares ICCBased color space structures and public constructors/helpers.

Defines:
- Opaque declarations for icclib types.
- `gs_cie_icc_s`, containing CIE common elements, component count/ranges, source stream identity, Lab/XYZ PCS flag, ICC profile pointer, lookup pointer, and icclib file wrapper pointer.
- `private_st_cie_icc` descriptor macro with finalization.
- `gs_cspace_build_CIEICC`
- `gx_load_icc_profile`
- `gx_increment_cspace_count`

The header explains why ICC profile and lookup objects live outside GC-managed memory and why stream identity must be validated. It also documents a known API bug: constructed CIE spaces start with reference count 1, so clients may need to decrement after installing.
