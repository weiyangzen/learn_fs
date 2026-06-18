# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/rdjpgcom.c

This is a standalone IJG utility that prints textual JPEG COM markers, with optional verbose frame information. It is intentionally a small example of marker parsing rather than a full decoder.

The program reads from one optional input file or stdin in binary mode. It defines JPEG marker constants, low-level byte readers, `first_marker()` for SOI validation, `next_marker()` for scanning marker boundaries before compressed data, and `skip_variable()` for uninteresting variable-length marker payloads.

`process_COM()` reads a COM-like marker segment, validates its length, normalizes CR/LF newline variants, escapes backslash, prints printable characters directly, and emits nonprintable bytes as octal escapes. In verbose mode, APP12 marker contents are also printed through this same routine.

`process_SOFn()` parses SOF markers to print image dimensions, component count, sample precision, and process type such as Baseline, Progressive, Lossless, or arithmetic-coded variants. It validates the SOF payload length and consumes per-component metadata.

`scan_JPEG_header()` walks markers from SOI until SOS or EOI. It handles SOF markers, COM, APP12, SOS, EOI, and skips everything else as variable-length marker data. It deliberately stops before compressed entropy-coded data because byte-stuffed `FF/00` sequences require different parsing.

Command-line parsing supports `-verbose` with abbreviation matching through `keymatch()`. `usage()` reports syntax and exits. Portability conditionals handle Macintosh command-line acquisition, binary stdin reopening, setmode, VMS binary modes, and exit-code definitions.

This file depends only on `jinclude.h`, stdio, ctype, and small platform conditionals; it does not link through the libjpeg decompressor API. Its main risks are typical standalone parser constraints: it assumes unknown pre-SOS markers have length fields and is designed for comment extraction, not full JPEG validation.
