# File Research: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/jcsample.c

Compression downsampler module.

Key points:
- Defines row groups as `max_v_samp_factor` input rows producing `v_samp_factor` output rows per component.
- `expand_right_edge` pads rows horizontally by duplicating rightmost samples to DCT-block width.
- `sep_downsample` applies one selected per-component downsample method to each component independently.
- Implements arbitrary integral-ratio box-filter downsampling, full-size copy/pad, common h2v1 and h2v2 downsampling with alternating rounding bias, and optional smoothed h2v2/full-size downsampling.
- Smoothing uses context rows and fixed-point weighted sums intended for dither cleanup.
- `jinit_downsampler` allocates the downsampler, rejects unsupported CCIR601 sampling, selects a per-component method from sampling-factor ratios, requests context rows when smoothing requires them, and warns when smoothing cannot apply to all components.

Dependencies and interactions:
- Called by `jcprepct.c`.
- Uses sampling factors and component dimensions established by `jcmaster.c`.

Risk notes:
- Fractional sampling ratios and CCIR601 sampling are not implemented.
- Arbitrary integral-ratio path is generic but not optimized for uncommon factors.
- Smoothing is limited to full-size and h2v2 cases.
