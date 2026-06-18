# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxmatrix.h

Internal Ghostscript matrix/fixed-point transformation header.

Key contents:
- Defines `PRECISE_CURRENTPOINT` as enabled.
- Defines `gs_matrix_fixed`, a matrix with cached fixed-point translation and a validity flag.
- Declares conversion from plain matrix to fixed matrix and point/distance transforms to fixed point.
- Declares a rounded fixed-point transform when precise currentpoint support is enabled.
- Defines `fixed_coeff`, used to avoid floating point in selected coordinate transforms.
- Declares `fixed_coeff_mult` and defines `m_fixed`, a macro that chooses a faster integer path when a fixed value is in range.

Notable dependencies:
- Plain matrix definitions from `gsmatrix.h`.

Research notes:
- The comments warn that disabling precise currentpoint should not go to production because it drops clamping.
- The fixed coefficient machinery is specialized and primarily called out for Type 1 font interpreter use.
