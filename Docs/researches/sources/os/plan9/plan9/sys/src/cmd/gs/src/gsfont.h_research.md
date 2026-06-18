# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsfont.h

## Role

Public generic font and font-cache interface.

## Main API

Declares font directory allocation, `gs_definefont`, similar-font lookup, `gs_scalefont`, `gs_makefont`, font state accessors, font purge, font lookup by ID, and cache parameter getters/setters.

## Main Types

Forward-declares `gs_font_dir`, `gs_font`, and `gs_matrix`.

## Contract

`gs_definefont` is intended only for original unscaled fonts. `gs_scalefont` and `gs_makefont` return `0` when a cached scaled font is reused and `1` when a new font is created.

## Dependencies

Uses `gs_memory_t`, `gs_state`, `gs_id`, and matrix/font structures from Ghostscript core headers.
