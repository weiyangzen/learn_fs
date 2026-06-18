# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jdatasrc.c

Stdio source manager for JPEG decompression.

Key behavior:
- Wraps an application-provided `FILE *` with a `jpeg_source_mgr`.
- Allocates a permanent 4096-byte input buffer so image sequences can be read from the same stream without losing buffered bytes.
- `fill_input_buffer` reads with `JFREAD`, treats an empty file as fatal, and injects a fake EOI marker with warning on later EOF/truncation.
- `skip_input_data` skips buffered bytes and refills as needed, using a simple stream-friendly implementation rather than `fseek`.
- Uses the library's default restart resynchronization method.
- `term_source` is a no-op; stream cleanup remains the caller's responsibility.

Dependencies:
- Uses C stdio through IJG `JFREAD`, decompressor source manager callbacks, error handling, and default restart resync.

Notable risks:
- This source manager is non-suspending; `skip_input_data` assumes `fill_input_buffer` never returns `FALSE`.
- Truncated nonempty files may produce partial output after fake EOI insertion.
- Reusing one JPEG object with a different source manager is unsafe for the same private-object-size reason as the destination manager.
