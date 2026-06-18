# File Research: sources/virtualization/nbdkit/server/log-fp.c

Purpose: Emits formatted nbdkit error messages to a `FILE *` target such as stderr or a configured log file.

Behavior:
- `log_fp_verror(fp, orig_errno, fs, args)` optionally locks the stream with `flockfile`.
- Applies red terminal color when the destination is a tty.
- Prefixes messages with program name, optional process name, optional thread-local name and instance number, then `error:`.
- Restores `errno = orig_errno` before `vfprintf` so `%m` expands correctly.
- Appends newline, restores terminal color, flushes the stream, and unlocks where supported.

Dependencies:
- Uses thread-local identity helpers and global `process_name`.
- Used by `log.c` according to the selected log sink.
