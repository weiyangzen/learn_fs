# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jcsample.c

Compression downsampling module.

Key behavior:
- Defines row-group semantics: `max_v_samp_factor` input rows produce each component's `v_samp_factor` output sample rows.
- Provides per-component downsampling methods: full-size copy, arbitrary integral box filtering, h2v1 averaging, h2v2 averaging, and optional smoothing variants.
- Performs horizontal edge expansion by duplicating rightmost samples.
- Uses alternating rounding bias in h2v1/h2v2 cases to reduce systematic rounding bias.
- Optional smoothing uses neighboring context rows and integer-scaled weights based on `smoothing_factor`.
- `jinit_downsampler` validates sampling ratios, rejects unsupported fractional sampling and CCIR601 sampling, assigns component-specific method pointers, and advertises whether context rows are needed.

Dependencies:
- Uses component sampling factors and image geometry from compressor setup.
- Cooperates with `jcprepct.c`, which supplies context rows and vertical padding.

Notable risks:
- CCIR601 sampling is explicitly not implemented.
- Smoothing is only available for full-size and h2v2 paths; unsupported smoothing combinations produce a trace warning and fall back without smoothing.
- Arbitrary integral downsampling exists but comments note it is not optimized for uncommon ratios.
