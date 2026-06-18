# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxmatrix.h

Internal Ghostscript matrix/fixed-point transformation header.

Key contents:
- Defines `PRECISE_CURRENTPOINT` as enabled.
- Defines `gs_matrix_fixed`, a matrix with cached fixed-point translation values and a validity flag.
- Declares conversion from plain matrix to fixed matrix and coordinate/distance transforms to fixed point.
- Declares rounded fixed-point point transformation when precise currentpoint support is enabled.
- Defines `fixed_coeff`, used to avoid floating point in selected coordinate transformations.
- Declares `fixed_coeff_mult` and defines `m_fixed`, a macro that chooses a faster integer path when the fixed value is in a safe range.

Notable dependencies:
- Plain matrix definitions from `gsmatrix.h`.

Research notes:
- Comments warn that disabling precise currentpoint should not go to production because it drops clamping.
- Fixed coefficient machinery is specialized and called out as primarily used by the Type 1 font interpreter.
