# File Research: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/jdmerge.c

Optional merged upsampling and YCbCr-to-RGB color conversion for common decompression cases.

Key points:
- Compiled only when `UPSAMPLE_MERGING_SUPPORTED` is enabled.
- Combines simple chroma replication with color conversion, reducing repeated chroma contribution calculations.
- Supports only YCbCr-to-RGB with 2h1v or 2h2v sampling, no fancy upsampling, no CCIR601 alignment, and no upsample-time scaling.
- Builds the same fixed-point YCbCr-to-RGB tables as `jdcolor.c`.
- `merged_2v_upsample` emits two rows per row group when possible and uses a spare row if the client output buffer accepts only one row or the image has an odd final row.
- `merged_1v_upsample` handles the one-output-row case without spare buffering.
- `h2v1_merged_upsample` and `h2v2_merged_upsample` compute chroma-derived RGB offsets once per chroma sample and apply them to paired/four Y samples.

Dependencies and interactions:
- Selected only by `jdmaster.c` after capability checks.
- Replaces separate `jdcolor.c` and `jdsample.c` work for matching cases.

Risk notes:
- The initializer trusts `jdmaster.c`; it does not revalidate capabilities locally.
- Output width may be odd, so both merged kernels contain explicit final-column handling.
- This path implements box-filter upsampling only, so fancy upsampling must disable it.
