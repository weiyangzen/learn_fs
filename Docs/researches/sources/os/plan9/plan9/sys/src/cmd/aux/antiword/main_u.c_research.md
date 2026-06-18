# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/main_u.c

Unix command-line entry point for `antiword`.

Responsibilities:

- Prints usage and version/help text.
- Parses command-line options with `iReadOptions()`.
- Supports `-` as stdin by copying stdin to `tmpfile()` in `pStdin2TmpFile()`.
- Processes each input in `bProcessFile()`:
  - opens file/stdin temp,
  - gets size,
  - guesses Word version,
  - rejects RTF/WordPerfect/non-Word,
  - creates output diagram,
  - runs `bWordDecryptor()`,
  - destroys diagram and closes file.
- Handles locale setup:
  - UTF-8 output may set `LC_CTYPE` from environment when supported,
  - otherwise falls back to normal locale or `C`.
- Handles multi-file text output by printing filename separators.
- Handles XML output by writing a DocBook prologue and optional `<set>` wrapper.
- On DOS builds, switches stdout to binary for PDF output and stdin to binary while copying.

Exit status is success only if at least one file was successfully processed. This is the normal non-GUI entry point in Unix-like builds, including the Plan 9-oriented source tree variant.
