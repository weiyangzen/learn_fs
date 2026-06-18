# File Research: sources/os/plan9/9front/sys/src/cmd/aux/antiword/main_u.c

This file is the Unix/DOS/NLM command-line entry point for `antiword`.

Key routines:
- `vUsage()` prints program metadata and supported switches.
- `pStdin2TmpFile(...)` copies standard input into a temporary seekable file.
- `bProcessFile(...)` opens a file or stdin, gets size, detects Word version, rejects RTF/WordPerfect/non-Word inputs, creates a diagram, runs `bWordDecryptor`, destroys the diagram, and reports success.
- `main(...)` parses options, configures locale, emits XML prologue/set wrappers when needed, processes all input files, and returns success only if at least one file succeeded.

Important behavior:
- `-` means read Word data from stdin.
- Multiple text outputs get filename separator banners.
- XML output emits a DocBook doctype and wraps multiple documents in `<set>`.
- UTF-8 locale is set only when the platform/environment and requested encoding support it.
- DOS mode switches stdin/stdout binary mode where needed.

Dependencies:
- Option parsing, basename/path helpers, locale helpers, Word detector/decryptor, diagram lifecycle, conversion options.

Role in antiword:
- Portable CLI wrapper around the shared Word decoding/rendering core.
