# File Research: sources/virtualization/libguestfs/daemon/proto.c

Core daemon protocol implementation.

Important behavior:
- `main_loop` reads length-prefixed XDR messages, validates program/version/direction/status, sets global `proc_nr`, `serial`, `progress_hint`, and `optargs_bitmask`, then dispatches.
- Errors are encoded by `send_error` with bounded error message length and errno string mapping.
- `reply` serializes normal replies and converts oversized reply-body encoding failures into daemon errors.
- `receive_file` consumes FileIn chunks, supports library cancellation, and invokes a write callback.
- `cancel_receive` sends cancellation back and drains incoming chunks.
- `send_file_write` sends FileOut chunks and checks for library-side cancellation.
- Progress notifications are rate-limited; pulse mode uses `SIGALRM` and an async-safe prebuilt XDR byte layout when timers/signals exist.

Filesystem relevance: every streamed file, directory, image, and command-output transfer depends on this chunk/cancel/progress machinery.
