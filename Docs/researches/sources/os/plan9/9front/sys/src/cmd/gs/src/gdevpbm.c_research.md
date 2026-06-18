# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpbm.c

## Purpose

`gdevpbm.c` implements Ghostscript output devices for the Netpbm family and a Plan 9 bitmap variant: PBM, PGM, PPM, automatic PNM variants, faux CMYK-to-PPM/CMYK-separation modes, PAM CMYK, and `plan9bm`.

## Main Devices

The shared device type is `gx_device_pbm`, a printer device with Netpbm-specific state: output magic number, optional header comment, raw/plain selector, optimization flag, observed color-use state, planar-buffer selection, and saved `copy_alpha`/`begin_typed_image` procs.

Exported devices include `gs_pbm_device`, `gs_pbmraw_device`, `gs_pgm_device`, `gs_pgmraw_device`, `gs_pgnm_device`, `gs_pgnmraw_device`, `gs_ppm_device`, `gs_ppmraw_device`, `gs_pnm_device`, `gs_pnmraw_device`, `gs_pkm_device`, `gs_pkmraw_device`, `gs_pksm_device`, `gs_pksmraw_device`, `gs_pam_device`, and `gs_plan9bm_device`. Most default to 72 DPI; `plan9bm` defaults to 100 DPI.

## Color Mapping and Parameters

PGM mapping converts RGB to gray and tracks whether output can remain black/white. PPM mapping packs component values according to device depth and tracks whether marks are black/white, gray, or color so optimized PNM devices can downshift their final file type. CMYK mapping packs CMYK component bits and maps them back to RGB for faux CMYK output. `ppm_get_params`/`ppm_put_params` add `UsePlanarBuffer` and support `GrayValues`, `RedValues`, `GreenValues`, and `BlueValues`, adjusting depth and dither counts within Ghostscript's supported power-of-two/depth constraints.

`ppm_open` uses `gdev_prn_open_planar`, marks the device separable/linear, initializes `uses_color`, and installs special procedures. `pnm_copy_alpha` and `pnm_begin_typed_image` conservatively update `uses_color` for alpha and image operations that might bypass simple RGB mapping.

## Output Flow

`pbm_print_page_loop` writes the appropriate header and iterates device rows via `gdev_prn_get_bits`, delegating row encoding to a format-specific function. For Netpbm formats it emits `P1` through `P7`; for Plan 9 bitmap (`magic == '9'`) it writes a Plan 9 rectangle-style header. PBM rows are written as packed raw bits or ASCII `0`/`1`; PGM rows handle 1/2/4/8/16-bit gray with optional inversion for subtractive planes; PPM rows write RGB tuples in raw or ASCII form.

The automatic variants use `uses_color` to emit PBM, PGM, or PPM from the same rendered buffer. `pkm_print_page` emits RGB from internally CMYK pixels. `psm_print_page` writes one PBM/PGM image per CMYK plane, using render-plane extraction and band-level color-use checks to skip empty planes efficiently. `pam_print_page` emits raw 32-bit CMYK PAM rows.

## Dependencies

The file relies on Ghostscript printer-device APIs, color-space/image metadata, planar rendering helpers, luminance weights, CMYK mapping helpers, and low-level bitmap row extraction. It also uses `gs_product` for generated comments.

## Filesystem Relevance

The file writes image files through `FILE *` streams supplied by Ghostscript printer infrastructure. It has no filesystem implementation or VFS behavior.

## Risks and Notes

The PGM RGB-to-gray function intentionally contains a compatibility kludge that sets `r`, `g`, and `b` all from `cv[0]`, preserving older DeviceN math behavior rather than ideal luminance conversion. Automatic color detection is conservative and may promote output to a richer format. Row encoders assume depths constrained by `ppm_put_params`; unsupported or inconsistent depths can produce malformed output or range errors elsewhere.
