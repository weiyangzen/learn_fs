# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/scfe.c

Implementation of Ghostscript’s `CCITTFaxEncode` stream filter.

Core behavior:

- Initializes raster size, input line buffer, encoded output buffer, optional previous-line buffer, and 1-D/2-D scheduling state.
- Buffers raw raster rows from the caller, pads/terminates each row with polarity changes for run detection, then emits encoded line data.
- Supports pure 1-D (`K == 0`), pure 2-D (`K < 0`), and mixed Group 3 1-D/2-D (`K > 0`) modes.
- Handles optional EOL emission, encoded byte alignment, and end-of-block EOL sequence generation.
- `cf_encode_1d` emits white/black run codes using CCITT Huffman tables.
- `cf_encode_2d` selects pass, vertical, or horizontal mode by comparing the current line against the previous reference line.
- `cf_put_long_run` emits makeup codes for long runs before termination codes.

Debug builds can count and print white/black run-code usage. This is CCITT fax image compression, not filesystem code.
