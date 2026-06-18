# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/wrjpgcom.c

Standalone IJG utility that inserts a textual COM marker into a JPEG stream.

Core marker logic:

- Defines minimal JPEG marker constants for SOI, EOI, SOS, SOFn variants, and COM.
- `first_marker()` validates the initial SOI bytes.
- `next_marker()` scans marker boundaries before compressed scan data, swallowing fill `0xFF` bytes and warning about discarded non-marker garbage.
- `copy_variable()` copies a variable-length marker payload, while `skip_variable()` discards one.
- `scan_JPEG_header()` copies markers up to the first SOFn or EOI, optionally removing existing COM markers.

Command-line behavior:

- Supports `-replace`, `-comment "text"`, and `-cfile name`, with abbreviated case-insensitive switch matching in `keymatch()`.
- Reads comment text from `-comment`, a file, or standard input, bounded by `MAX_COM_LENGTH`.
- Handles Unix one-file stdout style or `TWO_FILE_COMMANDLINE` platforms with explicit input/output names.
- Inserts the new COM marker just before the first SOFn marker so it follows JFIF/JFXX headers, then copies the remainder of the source file unchanged.

This utility is a small binary stream rewriter. It does not decode JPEG entropy data and does not depend on libjpeg compression/decompression objects.
