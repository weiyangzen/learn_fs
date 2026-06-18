# File Research: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/wrjpgcom.c

Standalone IJG utility for inserting a JPEG COM marker into a JFIF/JPEG stream. It performs minimal marker parsing and byte-copying without using the full JPEG library.

Main flow:
- `main` parses `-replace`, `-comment text`, and `-cfile name`, opens input and output streams, collects comment text if needed, calls `scan_JPEG_header`, emits a new COM marker, then copies the remainder of the source file.
- `scan_JPEG_header` copies SOI and all pre-SOF markers, optionally discarding existing COM markers, then stops at the first SOFn or EOI.
- `copy_variable` copies a variable-length marker segment after validating its length.
- `skip_variable` discards a variable-length segment.
- `copy_rest_of_file` byte-copies the remainder, including compressed data.

Important behavior:
- New comments are inserted just before SOFn so they appear after JFIF/JFXX APP markers and after any retained comments.
- `-replace` means pre-SOF COM markers are skipped; COM markers after SOF are not touched.
- Comment text may come from an argument, a file, or stdin and is capped by `MAX_COM_LENGTH` 65000.
- Includes DOS quote reassembly for `-comment` strings beginning with a quote.

Portability:
- Supports binary stdin/stdout setup, VMS open flags, Macintosh `ccommand`, optional two-file command-line mode, and abbreviated case-insensitive switches.

Filesystem relevance:
- Sequential read/write filter over JPEG bytes. No filesystem implementation content.
