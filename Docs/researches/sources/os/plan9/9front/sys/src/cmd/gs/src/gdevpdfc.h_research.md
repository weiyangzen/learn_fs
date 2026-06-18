# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpdfc.h

Internal cross-file interface for `pdfwrite` color-space writing, focused on CIE, Lab, and ICCBased color-space conversion.

Key contents:
- Defines `cie_cache_one_step_t` with `ONE_STEP_NOT`, `ONE_STEP_LMN`, and `ONE_STEP_ABC` to describe CIEBasedABC spaces that can be represented as one decode/cache step plus a matrix.
- Exports `pdf_finish_cie_space` from `gdevpdfc.c` for finalizing CIE-derived PDF dictionaries with white/black points.
- Declares `pdf_iccbased_color_space`, `pdf_convert_cie_space`, and `pdf_put_lab_color_space` from `gdevpdfk.c` for ICCBased copying/synthesis, CIE-to-Lab/ICCBased conversion, and Lab object creation.

Research notes:
- This is a narrow private header between `gdevpdfc.c` and `gdevpdfk.c`; it is not a broad public API.
- The enum is part of an optimization path that lets synthesized ICC profiles use TRC/XYZ tables instead of a sampled A2B lookup table when the CIE pipeline is simple enough.
