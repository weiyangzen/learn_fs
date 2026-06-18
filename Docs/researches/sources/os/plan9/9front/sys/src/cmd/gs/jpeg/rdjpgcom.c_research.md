# File Research: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/rdjpgcom.c

Standalone IJG utility for reading JPEG COM marker text from a JFIF/JPEG stream. It uses only stdio plus local marker parsing, not the full JPEG decompressor.

Main entry points and flow:
- `main` parses `-verbose`, opens one optional input file or stdin in binary mode, then calls `scan_JPEG_header`.
- `first_marker`, `next_marker`, `read_1_byte`, and `read_2_bytes` implement minimal marker stream parsing before compressed scan data.
- `scan_JPEG_header` walks markers until SOS or EOI, prints COM markers, optionally prints APP12 text and SOFn image dimensions.
- `process_COM` normalizes CR/LF forms, doubles backslashes, prints printable bytes directly, and octal-escapes nonprintable bytes.
- `process_SOFn` decodes common SOF marker names and validates the SOF segment length against component count.

Important behavior:
- It intentionally stops before SOS because the compressed entropy stream contains byte-stuffed FF/00 sequences that this simple parser cannot handle.
- Unknown variable-length markers are skipped via their 16-bit segment length.
- Garbage before a marker is skipped with a warning.
- Existing COM data is treated as textual but not character-set decoded.

Dependencies and portability:
- Includes `jinclude.h` for IJG portability macros and supports `USE_SETMODE`, `USE_FDOPEN`, `USE_CCOMMAND`, VMS binary open forms, and abbreviated case-insensitive switches.

Filesystem relevance:
- No filesystem implementation logic; this is an image metadata inspection tool in the Ghostscript-vendored JPEG utility tree. File IO is limited to sequential reads from a file/stdin.
