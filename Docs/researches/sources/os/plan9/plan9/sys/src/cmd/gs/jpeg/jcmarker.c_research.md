# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jcmarker.c

JPEG marker writer for compression output.

Key behavior:
- Emits low-level marker bytes and big-endian 16-bit marker fields through the destination manager.
- Writes DQT, DHT, optional DAC, DRI, SOF, SOS, JFIF APP0, Adobe APP14, SOI, EOI, and abbreviated table-only streams.
- Suppresses duplicate quantization and Huffman table emission using each table's `sent_table` flag.
- Chooses SOF0, SOF1, SOF2, or SOF9 based on baseline/progressive/arithmetic/precision state.
- Emits scan-specific Huffman tables, respecting progressive scans where only DC or AC tables are used.
- Exposes application marker insertion through `write_marker_header` and `write_marker_byte`.

Dependencies:
- Uses `jpeg_marker_writer`, destination manager callbacks, component tables, scan parameters, and IJG marker/table structures.

Notable risks:
- Marker writing does not support suspension; callers must ensure enough destination buffer space around header/trailer marker emission.
- Images wider or taller than 65535 are rejected at SOF emission.
- Arithmetic marker support is conditionally compiled, but compressor initialization elsewhere rejects arithmetic coding in this tree.
