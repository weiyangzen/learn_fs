# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxline.h

Private Ghostscript line parameter definitions.

Key contents:
- Defines `gx_dash_params`, including dash pattern storage, offset, adaptive flag, and computed dash state.
- Defines `gx_line_params`, including half-width, cap/join, curve join override, miter limit/check, dot length/orientation, and dash parameters.
- Provides macros for setting/current line width, miter limit access, dash adapt flag, and default initializers.
- Declares setters for miter limit, dash pattern, and dot length.

Notable dependencies:
- Public line parameter types from `gslparam.h`.
- Matrix type from `gsmatrix.h`.

Research notes:
- `gx_dash_params` is embedded in `gx_line_params` rather than intended for standalone allocation.
- The default miter check constant is precomputed and tied to `gx_set_miter_limit` / stroke behavior.
