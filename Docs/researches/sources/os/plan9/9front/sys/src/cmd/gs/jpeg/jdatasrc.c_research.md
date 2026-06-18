# File Research: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/jdatasrc.c

Standard stdio source manager for JPEG decompression input.

Key points:
- Defines a permanent `jpeg_source_mgr` wrapper around a caller-owned `FILE *`, a 4096-byte input buffer, and a `start_of_file` flag.
- `init_source` resets only the empty-file detection flag, deliberately preserving buffered bytes so multiple JPEG images can be read from one stream.
- `fill_input_buffer` reads via `JFREAD`, treats an empty file as fatal, but converts premature EOF after some data into a warning plus a synthetic EOI marker.
- `skip_input_data` consumes bytes from the current buffer and repeatedly refills as needed; it is simple stream-compatible skipping rather than `fseek`.
- `jpeg_stdio_src` allocates the source object and buffer in the permanent pool on first use, installs methods, and primes the manager with zero buffered bytes.

Dependencies and interactions:
- Used by applications before `jpeg_read_header`.
- Installs `jpeg_resync_to_restart` from `jdmarker.c` as the default restart resynchronizer.
- Not a core module; includes public headers plus `jerror.h`.

Risk notes:
- This source manager does not support input suspension because `fill_input_buffer` always returns `TRUE`.
- Mixing this source manager with a differently sized manager on the same decompression object is unsafe because its private object is permanent.
- Premature EOF recovery can produce partial image output with warnings rather than failing immediately.
