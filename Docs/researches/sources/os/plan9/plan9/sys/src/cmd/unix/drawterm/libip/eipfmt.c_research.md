# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libip/eipfmt.c

Implements Plan 9 `Fmt` conversions for Ethernet and IP addresses.

Key function:
- `eipfmt`: handles `%E`, `%I`, `%i`, `%V`, and `%M`.

Important behavior:
- IPv4-mapped IPv6 addresses print as dotted quad.
- IPv6 formatting performs longest zero-run elision.
- Masks print as `/prefix` only when the mask is a valid contiguous prefix; otherwise they fall back to full IP formatting.
