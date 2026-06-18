# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/scfx.h

Defines CCITTFax stream state structures for encode and decode filters. The common state stores fax parameters such as `Uncompressed`, `K`, EOL/byte-alignment flags, dimensions, block termination, polarity, damaged-row tolerance, bit order, decoded alignment, row buffers, raster size, and mixed-mode row counter.

Encode state adds encoded-line buffer fields and copy counters. Decode state adds bit position, rows/row counters, input/output row positions, EOL count, polarity inversion, 2-D run state, damaged-row tracking, and placeholders for uncompressed runs.

Dependencies include `shc.h`, `strimpl.h`, and the templates implemented in `scfe.c`/`scfd.c`.

This header is the contract between CCITTFax parameter handling and filter implementations.
