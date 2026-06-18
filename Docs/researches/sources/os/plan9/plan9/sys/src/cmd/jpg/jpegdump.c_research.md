# File Research: sources/os/plan9/plan9/sys/src/cmd/jpg/jpegdump.c

## Purpose
Standalone JPEG marker dumper/parser by Tom Szymanski.

## Behavior
Reads a JPEG file with stdio, walks marker segments, and prints SOI, EOI, APP, COM, DQT, DHT, SOF, SOS, restart, and entropy sequence information. `-t` prints quantization and Huffman table contents.

## Implementation
Uses byte readers `get1`/`get2`, segment-specific parsers, and scans entropy-coded data by counting bytes and stuffed `0xff00` markers until the next marker.

## Dependencies
Uses ISO C headers rather than Plan 9 libc interfaces. It is diagnostic tooling, not part of the runtime decoder.
