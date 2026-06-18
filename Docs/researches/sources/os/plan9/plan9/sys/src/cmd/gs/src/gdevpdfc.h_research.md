# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpdfc.h

Private cross-file interface for PDF color-space writing, focused on CIE, Lab, and ICCBased conversion.

Key contents:
- Defines `cie_cache_one_step_t` with `ONE_STEP_NOT`, `ONE_STEP_LMN`, and `ONE_STEP_ABC`.
- Exports `pdf_finish_cie_space` from `gdevpdfc.c`.
- Declares `pdf_iccbased_color_space`, `pdf_convert_cie_space`, and `pdf_put_lab_color_space` from `gdevpdfk.c`.

Research notes:
- This header is a narrow contract between `gdevpdfc.c` and `gdevpdfk.c`.
- The enum identifies simple CIE pipelines that can be represented with TRC/XYZ ICC tables instead of a sampled lookup table.
