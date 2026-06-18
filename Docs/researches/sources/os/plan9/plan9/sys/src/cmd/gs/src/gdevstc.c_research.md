# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevstc.c

Purpose: Main Ghostscript Epson Stylus Color / ESC/P2 printer driver.

Key behavior:
- Defines `stcolor`, defaulting to a CMYK direct 360x360 dpi printer device with configurable margins.
- Maintains a table of dithering algorithms: built-ins `gscmyk`, `hscmyk`, plus algorithms declared in `gdevstc.h` (`gsmono`, `gsrgb`, `fsmono`, `fsrgb`, `fsx4`, `fscmyk`, `fs2`).
- Builds default ESC/P2 initialization and release command strings when user params do not provide them.
- Main `stc_print_page` allocates scanline, algorithm, dither buffer, printer line buffers, seed rows, and ESC/P2 command buffer.
- Reads Ghostscript scanlines, detects white rows, converts input depth to algorithm data, invokes dithering, splits output into mono/RGB/CMYK printer planes, and emits printer bands.
- Supports plain, run-length, and delta-row output encodings.
- Implements software weave/multipass printing, single-pass bands, and delta-row printing.
- Builds ESC/P2 positioning/color/data commands, including color selection and linefeed adjustments.
- Generates transfer/code lookup arrays from user-provided coding/transfer curves and optional color adjustment matrices.
- Dynamically installs appropriate color mapping procs for gray, RGB, CMYK, or special CMYK10 modes.
- Provides parameter get/put support for version, algorithm list, model, output coding, weave flags, ESC/P2 control values, custom init/release strings, color adjustment matrix, and component coding/transfer arrays.
- Includes built-in direct 1-bit CMYK splitting (`stc_gscmyk`) and experimental CMYK10 halftone/dither (`stc_hscmyk`).

Important dependencies:
- Shared declarations and algorithm registry in `gdevstc.h`.
- Algorithm implementations in `gdevstc1.c`, `gdevstc2.c`, `gdevstc3.c`, and `gdevstc4.c`.
- Ghostscript printer, parameter, and device color APIs.

Notable risks / findings:
- `stc_freedata(gs_memory_t *mem, stc_t *stc)` references `sd->stc.alg_item` even though `sd` is not in scope, which appears to be a compile-time defect in this source as read.
- Many error paths manually unwind allocations; this file is high-risk for leaks or stale pointers if modified.
- `put_params` mutates complex device state, then conditionally restores or frees old state; changes here need careful open/close lifecycle testing.
