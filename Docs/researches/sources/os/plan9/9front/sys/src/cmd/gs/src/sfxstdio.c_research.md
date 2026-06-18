# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/sfxstdio.c

Implements file streams using the C stdio library.

Key points:
- `sread_file`, `swrite_file`, and `sappend_file` initialize Ghostscript streams around `FILE *` handles.
- Seekability is probed with `ftell`/`fseek`, with `clearerr` used to undo probe side effects.
- `sread_subfile` restricts reusable streams to a logical subfile by setting `file_offset` and `file_limit`.
- Read processing uses `fread`, EOF/error checks, file limit handling, and interrupt processing.
- Write processing uses `fwrite`, handles zero-count writes specially for broken libraries, and flushes with `fflush`.
- `s_file_switch` changes a file stream between read and write modes while preserving logical stream position and append-mode state.

Dependencies and interactions:
- Provides the same public stream backend interface as `sfxfd.c`.
- Uses standard Ghostscript stream procedure tables.

Research relevance:
- This is the portable C-library file I/O backend for Ghostscript streams.
