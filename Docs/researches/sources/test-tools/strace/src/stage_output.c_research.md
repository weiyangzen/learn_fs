# sources/test-tools/strace/src/stage_output.c

Purpose: provides staged syscall output buffering so partially decoded output can be published only on success or dropped on failure.

Important APIs/types/functions: `struct staged_output_data`, `strace_open_memstream`, `strace_close_memstream`, `open_memstream`, `tcp->outf`, and `tcp->staged_output_data`.

Control flow: when `HAVE_OPEN_MEMSTREAM` is available, open allocates staging data, opens a dynamic memory stream, flushes it once so buffer pointers are initialized, saves the real output stream, and redirects `tcp->outf`. Close restores the real stream, optionally writes the staged buffer to it, otherwise logs a debug drop, then frees buffer and staging data. Without `open_memstream`, functions effectively return `NULL`/do nothing.

State and persistence behavior: mutates per-tcb output stream state while staging is active. Cleanup resets `tcp->staged_output_data` to `NULL` and frees all allocated memory.

Dependencies and integration points: used by decoders that cannot know until exit whether staged output should be emitted. Depends on libc `open_memstream` availability and strace error/debug helpers.

Risks: unbalanced open/close would leave `tcp->outf` redirected or leak memory. Nested staging is not supported by this structure. `fclose`/`fflush` failures are reported but staged output may be lost.

Test signals: publish and drop paths, double-close debug path, `open_memstream` failure handling if injectable, and build without `HAVE_OPEN_MEMSTREAM`.
