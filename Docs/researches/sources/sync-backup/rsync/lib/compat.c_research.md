# sources/sync-backup/rsync/lib/compat.c

Purpose: implements small portability replacements and human-readable number formatting helpers used across rsync.

Important APIs/types/functions: `get_number_separator`, `get_decimal_point`, optional fallback `getcwd`, optional fallback `waitpid`, optional fallback `memmove`, optional fallback `strpbrk`, optional fallback `strlcpy`, optional fallback `strlcat`, `sys_gettimeofday`, `do_big_num`, and `do_big_dnum`. Static `number_separator` caches the inferred thousands separator.

Control flow: configure macros include only missing libc replacements. `get_number_separator` formats `3.14` and chooses the opposite character of the locale decimal point for grouping. `do_big_num` rotates through four static buffers, optionally scales values into K/M/G/T/P units for human modes, otherwise emits digits backward with optional group separators and fractional suffix. `do_big_dnum` formats a double, and for human mode delegates integer/grouped rendering to `do_big_num`.

State and persistence behavior: state is limited to static formatting buffers and cached separator. Results are overwritten after four `do_big_num` calls or the next `do_big_dnum` call, so callers must copy if they need longer-lived strings. No persistent storage.

Dependencies/integration: includes `rsync.h` and `itypes.h`; used by logging, stats, and user-facing output helpers such as `big_num`. The portability shims integrate with configure results and old Unix libc behavior.

Risks/test signals: static buffers are not thread-safe, but rsync is process-oriented. `strlcat` assumes `bufsize - 1` is safe, so zero-size calls rely on unsigned behavior and should be tested if used. Human number formatting should be validated under locales with comma and dot decimal separators, negative `INT64_MIN`, and boundary values at 1000/1024 unit transitions.
