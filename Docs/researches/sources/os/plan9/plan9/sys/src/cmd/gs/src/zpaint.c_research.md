# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/zpaint.c

Painting operator glue. It maps `fill`, `eofill`, and `stroke` directly to `gs_fill`, `gs_eofill`, and `gs_stroke`.

It also exposes non-standard `.fillpage` and `.imagepath`. `.fillpage` fills the current page through `gs_fillpage`. `.imagepath` accepts width, height, and a readable bitmap string, checks that enough data is present for one bit per pixel, and passes the mask data to `gs_imagepath` to append an image-derived path.

The file is intentionally thin; validation is limited to operand types, data length, and graphics-library return codes.
