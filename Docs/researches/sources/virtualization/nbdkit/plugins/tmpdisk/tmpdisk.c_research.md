# File Research: sources/virtualization/nbdkit/plugins/tmpdisk/tmpdisk.c

Implements the `tmpdisk` plugin, creating a fresh temporary disk image per client connection and serving it through local file descriptor I/O.

Key behavior:
- `.load` defaults `tmpdir` from `TMPDIR` or `LARGE_TMPDIR`.
- `.config` requires `size`, optionally overrides `command`, rejects command-line `disk`, and forwards any valid shell-variable key/value into a linked list for the creation command.
- `.config_complete` requires `size`.
- `run_command` builds a shell script in memory, redirects stdin/stdout to `/dev/null`, assigns `disk`, `size`, and forwarded variables with shell quoting, appends the command string, and executes it with `system`.
- `.open` creates a private `mkdtemp` directory under `tmpdir`, constructs `<dir>/disk`, runs the mkfs/creation command, opens the resulting regular file or block device, determines true size with `device_size`, unlinks the disk path, removes the directory, and returns a handle containing the fd and size.
- `.pread`/`.pwrite` loop over `pread`/`pwrite` until the request is complete.
- `.flush` is a deliberate no-op because the disk is temporary.
- `.trim` uses `fallocate(FALLOC_FL_PUNCH_HOLE | FALLOC_FL_KEEP_SIZE)` when available. Advisory trim failures are ignored except `EPERM` and `EIO`; unsupported hole punching is cached per handle.
- `.can_fua` advertises native FUA but `.pwrite`, `.trim`, and `.flush` intentionally ignore persistence semantics.
- `.can_multi_conn` returns false because each connection has its own temporary disk and shared multi-conn semantics would be unsafe.
- Thread model is `NBDKIT_THREAD_MODEL_PARALLEL`.

Dependencies:
- nbdkit API v2.
- Common utilities: `shell_quote`, `is_shell_variable`, `device_size`.
- Generated `default-command.c`.

Notes and risks:
- `system` runs user-controlled `command` by design; variable names are restricted and values are shell-quoted.
- On `mkdtemp` success but later failure before opening, the temporary directory is not removed in the error path unless the fd was opened.
- FUA support is intentionally semantic no-op because data is temporary.
