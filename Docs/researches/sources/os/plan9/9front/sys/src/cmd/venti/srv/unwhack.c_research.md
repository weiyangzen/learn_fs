# File Research: sources/os/plan9/9front/sys/src/cmd/venti/srv/unwhack.c

`unwhack.c` implements decompression for Venti’s custom `whack` LZ-style format. It decodes literals with a recent-literal history optimization, decodes short and extended match lengths, decodes offset classes, copies matches from prior output, and reports detailed errors through `Unwhack.err`.

The decoder validates output bounds, offset range, bitstream underrun/overrun, and length range. It returns the exact uncompressed length on success or `-1` on malformed compressed data.

This must remain bit-compatible with `whack.c`; it is used when reading compressed clumps from arenas.
