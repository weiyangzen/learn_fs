# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jdapistd.c

Standard full-decompression public API.

Key behavior:
- `jpeg_start_decompress` initializes master decompression, optionally preloads multiple scans into the coefficient buffer, and prepares output passes.
- `output_pass_setup` handles dummy output passes needed for two-pass color quantization, then enters either scanline or raw-output state.
- `jpeg_read_scanlines` runs the main decompression pipeline into caller scanline buffers and advances `output_scanline`.
- `jpeg_read_raw_data` returns one raw iMCU row through the coefficient controller and requires caller capacity for a full iMCU row.
- Buffered-image mode APIs `jpeg_start_output` and `jpeg_finish_output` allow selecting and finishing output passes by scan number when multiscan support is compiled in.

Dependencies:
- Calls master decompression, input controller, main controller, coefficient controller, and optional progress monitor hooks.

Notable risks:
- Linking this file intentionally pulls in the full decompressor, unlike `jdapimin.c`.
- Multipass/multiscan and two-pass quantization paths are compile-time gated.
- Excess read calls after output completion warn and return zero rather than silently proceeding.
