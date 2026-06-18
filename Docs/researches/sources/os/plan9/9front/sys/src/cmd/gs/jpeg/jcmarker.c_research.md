# File Research: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/jcmarker.c

JPEG marker writer for compression.

Key points:
- Defines JPEG marker codes and a marker writer with `last_restart_interval` tracking.
- Low-level emitters write bytes, markers, and big-endian 16-bit values through the destination manager; marker-writing suspension is not supported.
- Emits DQT, DHT, optional DAC, DRI, SOF, SOS, JFIF APP0, Adobe APP14, arbitrary marker headers/bytes, SOI, EOI, and tables-only datastreams.
- `write_frame_header` emits needed DQT tables before SOF, determines baseline vs extended/progressive/arithmetic SOF marker, and warns on 16-bit quant tables in otherwise baseline files.
- `write_scan_header` emits needed entropy tables/conditioning, DRI if changed, then SOS.
- `write_file_header` emits SOI plus configured APP0/APP14; `write_tables_only` emits SOI, all unsent tables, and EOI.
- `jinit_marker_writer` installs all marker writer methods.

Dependencies and interactions:
- Used by `jcapimin.c`, `jcapistd.c`, `jcmaster.c`, and `jctrans.c`.
- Table `sent_table` flags from quant/Huffman table objects prevent duplicate marker output.

Risk notes:
- Applications using suspension must ensure buffer space for markers; this module errors if marker output cannot complete.
- Arbitrary marker APIs trust the caller to provide correct payload length and safe marker choice.
- SOF dimension fields cap emitted JPEG dimensions at 65535.
