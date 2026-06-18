# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/sdcte.c

Implements the `DCTEncode` stream filter around IJG libjpeg. It provides a JPEG destination manager that suspends when the output buffer fills, initializes compression, writes optional marker bytes, optionally writes an Adobe APP14 marker, streams scanlines, finishes compression into a fixed internal buffer, and drains final bytes.

The process routine is phase-driven from initialization through final EOFC. It checks that complete scanlines are available unless input is marked final, and returns output-full or input-needed statuses as required by Ghostscript stream conventions.

Dependencies include `jpeglib_.h`, `jerror_.h`, `sdct.h`, `sjpeg.h`, and Ghostscript memory/debug headers.

This is JPEG encoding stream glue, not filesystem code.
