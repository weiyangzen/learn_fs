# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevstc1.c

Sample monochrome “dithering” module for the Epson Stylus Color driver.

Key behavior:
- Implements `stc_gsmono`, selected with `-sDithering=gsmono`.
- Does not perform real dithering; it expects Ghostscript to supply 1-bit-like byte values.
- For normal scanline calls, copies input bytes directly to output.
- For white-line notification calls (`in == NULL`), clears the output line.
- For initialization calls (`npixel <= 0`), clears any allocated private buffer.
- Validates that the device has one component, uses byte algorithm values, and is not marked direct.

Notable dependencies:
- Shared Stylus Color driver definitions from `gdevstc.h`.

Research notes:
- The extensive comments document the dither callback calling convention used by all `stc` algorithms.
- This routine is mostly a reference/minimal algorithm.
