# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxtype1.h

Private definitions for the Adobe Type 1 / Type 2 charstring interpreter.

Key contents:
- Defines oversampling scale structures `pixel_scale` and `point_scale`, plus rounding helpers.
- Sets Type 2 total stem hint limit to 96.
- Defines `ip_state_t`, the interpreter control-stack frame containing instruction pointer, decryption state, and owning glyph data for GC.
- Defines encrypted/unencrypted charstring byte access macros.
- Forward-declares path and segment internals.
- Defines `gs_type1_state_s`, including:
  - Type 1 hinter state
  - font, imager state, output path, paint type, callback data
  - fixed CTM coefficients, flatness, origin, oversampling scale
  - operand stack and instruction stack
  - initialization, side-bearing, width, hint, `seac`, flex, and transient-array state
- Declares GC structure macro `public_st_gs_type1_state`.
- Defines operand-stack helper macros and number-decoding macros for 1-byte, 2-byte, and 4-byte charstring numbers.
- Declares shared interpreter utilities: finish init, side bearing/width, blend, `seac`, endchar, and metrics extraction.

Dependencies:
- Cryptography/decryption helpers from `gscrypt1.h`.
- Glyph data from `gsgdata.h`.
- Type 1 font definitions from `gstype1.h`.
- Type 1 hinting from `gxhintn.h`.

Research notes:
- The decode macros are low-level and assume the caller has valid charstring bounds/control flow.
- The state struct is shared by Type 1 and Type 2 interpreters, so it carries fields for both classic Type 1 operations and Type 2 transient/hint behavior.
