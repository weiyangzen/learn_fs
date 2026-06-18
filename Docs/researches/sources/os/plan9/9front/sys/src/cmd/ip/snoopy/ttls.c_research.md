# File Research: sources/os/plan9/9front/sys/src/cmd/ip/snoopy/ttls.c

This snoopy module decodes a small TTLS tunnel/framing header.

Key behavior:
- Parses a flags byte with version bits and S/M/L flags.
- If the L flag is set, consumes and prints a 32-bit total length.
- Always demuxes to `dump` so remaining payload is printed.
- Prints remaining data length and labels empty unflagged frames as acknowledgements.

Research notes:
- No filters are implemented.
- The module’s mux table contains only `dump` to force payload display.
