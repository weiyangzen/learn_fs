# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsicc.h

## Role

`gsicc.h` defines ICCBased color-space parameter structures and public constructor/loading helpers.

This is color-management API infrastructure, not filesystem code.

## Main Types And APIs

- Opaque forward declarations for icclib structures `_icc` and `_icmLuBase`, avoiding a hard dependency on `icc.h` for builds without ICC support.
- `gs_cie_icc`: CIE common prefix, component count/ranges, stream identity and pointer, PCS Lab flag, icclib profile pointer, lookup pointer, and icclib file wrapper pointer.
- `private_st_cie_icc()` descriptor macro includes finalization and tracks `instrp` for GC relocation.
- `gs_cspace_build_CIEICC`, `gx_load_icc_profile`, and `gx_increment_cspace_count`.

## Important Contract

The header documents that the profile stream remains a PostScript object subject to save/restore, GC relocation, closure, and reuse; therefore `file_id` plus lazy stream-pointer update are used to keep icclib access safe.

## Notable Risks

The constructor starts the CIE ICC structure with reference count 1, and the comments call this an API bug because clients must decrement after passing the color space into normal setters to avoid permanent allocation.
