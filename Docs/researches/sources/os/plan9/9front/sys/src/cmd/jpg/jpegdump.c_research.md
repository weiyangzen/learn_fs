# File Research: sources/os/plan9/9front/sys/src/cmd/jpg/jpegdump.c

This is a standalone JPEG marker parser/dumper, written in portable stdio C style.

Key behavior:
- Reads JPEG marker streams and prints SOI/EOI, SOF, SOS, DQT, DHT, DAC, COM, APPn, restart markers, and entropy segment lengths.
- `-t` dumps quantization and Huffman table entries.
- APP marker parsing extracts printable strings.
- Supports multiple JPEG streams concatenated in one file by restarting after EOI if more input remains.

Research notes:
- Uses custom `warn`, `quit`, and `fatal` routines.
- The SOI check is commented out, so parsing starts by searching marker structure rather than enforcing JFIF/SOI upfront.
