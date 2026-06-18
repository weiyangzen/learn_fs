# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/sdcte.c

Implementation of Ghostscript’s `DCTEncode` JPEG stream filter.

Core behavior:

- Defines IJG destination-manager callbacks; `empty_output_buffer` returns false to suspend when output is full.
- Defaults include empty markers and `NoMarker=true`.
- `s_DCTE_process` runs a phase machine:
  - Start JPEG compression.
  - Write supplied custom marker bytes.
  - Optionally write a manual Adobe APP14 marker carrying `ColorTransform`.
  - Feed scanlines from input to IJG compression.
  - Finish compression into a fixed internal buffer.
  - Copy final bytes to caller output and return `EOFC`.
- It validates premature input EOF during scanline consumption.
- `s_DCTE_release` destroys JPEG state, frees compression data, and restores the template pointer.

This is JPEG compression stream code, not filesystem logic.
