# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevfax.c

Fax output devices using Ghostscript CCITT Fax encoding streams.

Key behavior:
- Defines `faxg3`, `faxg32d`, and `faxg4`.
- Adds `AdjustWidth` parameter.
- Initializes `stream_CFE_state` with `BlackIs1`, page columns/rows, and optional legal fax width adjustment.
- Shared `gdev_fax_print_strip` streams scanlines through a CCITT encoder and writes compressed output.
- G3 1-D, G3 2-D, and G4 differ by `K`, EOL, and block settings.

Risks / notes:
- Special-cases output filename `nul`.
- Width may differ from device width after fax adjustment, so buffer sizing accounts for both.
