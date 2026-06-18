# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevstc1.c

Purpose: Simple monochrome “dithering” algorithm for `stcolor`, exposed as `gsmono`.

Key behavior:
- For positive `npixel`, copies byte input directly to output.
- For white-line notifications (`in == NULL`), clears the output line.
- For initialization calls (`npixel <= 0`), clears any algorithm buffer and validates that the device has one component, uses byte data, and is not direct.
- Intended to let Ghostscript perform the actual 1-bit monochrome work.

Important dependencies:
- `gdevstc.h` for device state, algorithm contract, and flags.

Notable risks / findings:
- Minimal algorithm; behavior is intentionally pass-through.
