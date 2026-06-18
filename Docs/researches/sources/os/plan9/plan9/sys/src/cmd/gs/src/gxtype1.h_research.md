# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxtype1.h

Private Type 1 / Type 2 charstring interpreter state and helper macro header.

Key contents:
- Defines oversampling scale structures `pixel_scale` and `point_scale`, plus `set_pixel_scale` and `scaled_rounded`.
- Sets `max_total_stem_hints` to 96 per Type 2 documentation.
- Defines `ip_state_t`, the saved instruction pointer/decryption/glyph-data state for charstring subroutine calls.
- Provides `charstring_this`, `charstring_next`, and `charstring_skip_next` macros for encrypted or plain CharString byte access.
- Defines `struct gs_type1_state_s`, including Type 1 hinter state, font/imager/path pointers, grid-fitting and paint state, fixed CTM coefficients, flatness, oversampling, operand stack, instruction stack, sidebearing/width metrics, Type 2 hint count, seac state, flex state, ignored pops, and transient array.
- Declares the public structure descriptor macro for GC integration.
- Defines operand-stack helper macros `CLEAR_CSTACK`, `INIT_CSTACK`, and `CS_CHECK_PUSH`.
- Defines number-decoding macros for 1-byte, 2-byte, and 4-byte charstring numbers.
- Declares shared interpreter utility functions: `gs_type1_finish_init`, `gs_type1_sbw`, `gs_type1_blend`, `gs_type1_seac`, `gs_type1_endchar`, and `type1_cis_get_metrics`.

Notable dependencies:
- Encryption: `gscrypt1.h`.
- Glyph data and Type 1 data structures: `gsgdata.h`, `gstype1.h`.
- Hinting: `gxhintn.h`.

Research notes:
- Operand and instruction stack sizes match Type 2 documentation: 48 operands and 10 call stack entries.
- The 4-byte decode path sign-extends only on platforms where `long` exceeds 4 bytes.
- This is a private interpreter header; it exposes many macros that assume local variables such as `csp`, `cstack`, `cip`, and decryption state.
