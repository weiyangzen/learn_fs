# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jdmarker.c

Purpose: JPEG marker parser and restart-marker recovery logic.

Key structures and routines:
- `JPEG_MARKER` enum defines SOF/SOS/DQT/DHT/DRI/APP/COM/RST marker codes.
- `my_marker_reader` extends `jpeg_marker_reader` with overridable COM/APPn processors and marker-saving state.
- Input macros `INPUT_VARS`, `INPUT_SYNC`, `INPUT_BYTE`, `INPUT_2BYTES` support suspension-safe parsing.
- `get_soi()`, `get_sof()`, `get_sos()`, `get_dac()`, `get_dht()`, `get_dqt()`, `get_dri()` parse core marker types.
- `examine_app0()` recognizes JFIF/JFXX APP0 metadata.
- `examine_app14()` recognizes Adobe APP14 metadata and transform flag.
- `get_interesting_appn()` inspects APP0/APP14 without saving the full marker.
- `save_marker()` optionally stores COM/APPn payloads in `marker_list`.
- `skip_variable()` skips unneeded variable-length markers.
- `next_marker()` finds the next marker after entropy data, warning about extraneous bytes.
- `first_marker()` enforces initial SOI.
- `read_markers()` dispatches marker handling until SOS, EOI, or suspension.
- `read_restart_marker()` verifies expected RSTn markers.
- `jpeg_resync_to_restart()` implements default recovery from missing/wrong restart markers.
- `reset_marker_reader()` and `jinit_marker_reader()` initialize parser state.
- `jpeg_save_markers()` and `jpeg_set_marker_processor()` expose marker customization hooks.

Important behavior:
- Designed for suspending data sources; marker parameters are reprocessed after suspension unless saving-marker state has advanced the restart point.
- Rejects unsupported SOF types such as lossless/differential modes.
- Parses DQT values from zigzag order into natural order.
- Minimal DHT validation occurs here; deeper Huffman validation occurs in `jdhuff.c`.
- Ignores DNL by skipping it, while zero image dimensions are rejected at SOF.
- APP0 and APP14 are interpreted even when not saved, because they affect density/colorspace transform assumptions.

Dependencies:
- Source manager callbacks `fill_input_buffer`, `skip_input_data`, `resync_to_restart`.
- JPEG memory manager, quant/Huffman table allocation, error/trace macros.

Notes:
- This is one of the main robustness boundaries for malformed JPEG streams.
