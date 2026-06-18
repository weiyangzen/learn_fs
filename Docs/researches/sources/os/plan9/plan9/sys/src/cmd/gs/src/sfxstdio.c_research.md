# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/sfxstdio.c

Default Ghostscript file stream backend using ANSI stdio.

Key behavior:
- `sread_file`, `swrite_file`, and `sappend_file` initialize streams around `FILE *`.
- Read initialization probes seekability with `ftell`/`fseek` and clears probe-induced error state when appropriate.
- `sread_subfile` confines an existing seekable read stream to a logical byte range.
- Read processing uses `fread`, honors `file_limit`, returns `EOFC` on EOF, and processes Ghostscript interrupts.
- Write processing uses `fwrite`, flush uses `fflush`, and close flushes pending stream data before closing the file.
- `s_file_switch` switches a bidirectional stream between read/write modes while preserving logical position.

Notable dependencies:
- `stream.h`, `strimpl.h`, `gpcheck.h`.
- C stdio wrappers via `stdio_.h`.

Research notes:
- This is the portable baseline compared with the direct-file-descriptor variant.
- The stream mode/procedure setup mirrors `sfxfd.c`, making the two backends interchangeable at the higher stream layer.
