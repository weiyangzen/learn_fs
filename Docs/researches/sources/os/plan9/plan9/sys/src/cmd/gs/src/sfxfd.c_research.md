# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/sfxfd.c

Alternative file stream backend using direct OS file-descriptor calls while retaining a `FILE *` interface.

Key behavior:
- `sread_fileno`, `swrite_fileno`, and `sappend_fileno` initialize Ghostscript streams backed by `read`, `write`, `lseek`, and `fsync`.
- Read support detects seekability by probing `lseek`, supports subfile limits, implements `available`, seeks within the current buffer when possible, and retries interrupted/nonblocking reads for `EINTR`, `EAGAIN`, and `EWOULDBLOCK`.
- Write support flushes with `s_process_write_buf`, calls `fsync` on flush, handles zero-length writes specially, retries transient write errors, and supports append positioning.
- `s_fileno_switch` switches an update-mode stream between reading and writing while preserving current logical position and append mode.

Notable dependencies:
- Platform wrappers: `unistd_.h`, `errno_.h`.
- Ghostscript stream internals: `stream.h`, `strimpl.h`, `gpcheck.h`.

Research notes:
- Comments warn this may not compile unchanged on non-Unix platforms.
- With `KEEP_FILENO_API`, public names are renamed so this can coexist with `sfxstdio.c`.
- The backend aggressively syncs on flush, which is stronger and more expensive than the stdio backend.
