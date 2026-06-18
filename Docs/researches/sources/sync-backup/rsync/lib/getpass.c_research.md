# sources/sync-backup/rsync/lib/getpass.c

Purpose: implements `getpass` on systems that lack it, reading a password from `/dev/tty` or standard input while attempting to disable terminal echo and signal characters.

Important APIs/types/functions: public `getpass(const char *prompt)` and static `password[256]` buffer.

Control flow: the function opens `/dev/tty` for read/write and falls back to `stdin`/`stderr` if unavailable. It saves terminal attributes, clears `ECHO` and `ISIG`, prints a warning if echo could not be disabled, prompts, reads one line with `fgets`, prints a newline, restores terminal settings, closes the tty if opened, strips a trailing newline, and returns the static buffer or `NULL`.

State and persistence behavior: password contents persist in a static buffer until overwritten by the next call or process exit. No explicit zeroing is performed. Terminal state is restored on the normal path after reading.

Dependencies/integration: includes `stdio.h`, `string.h`, `termios.h`, and `rsync.h` for `BOOL`, `True`, and `False`. Used by authentication/password prompting code on deficient libc platforms.

Risks/test signals: fixed 256-byte buffer truncates longer passwords, disabling `ISIG` changes Ctrl-C behavior while reading, and abnormal termination before restore could leave terminal settings modified. Tests should use pseudo-terminals to verify echo restore, stdin fallback, newline stripping, EOF handling, and truncation behavior.
