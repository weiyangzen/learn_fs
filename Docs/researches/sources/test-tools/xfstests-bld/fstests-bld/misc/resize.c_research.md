# sources/test-tools/xfstests-bld/fstests-bld/misc/resize.c

## Purpose

`sources/test-tools/xfstests-bld/fstests-bld/misc/resize.c` is a small terminal-size discovery and update helper derived from xterm's `resize.c` and simplified for kvm-xfstests. It talks directly to the controlling terminal, asks the terminal emulator for its cursor-position response after moving to a very large row/column, then uses the answer to set the kernel's terminal window size with `TIOCSWINSZ`. It also prints shell-style `COLUMNS=` and `LINES=` assignments for consumers that want to update their environment.

The source was read as a complete 207-line C file for this report.

## Important APIs, Types, and Functions

Important constants and globals: `ESCAPE(string)` builds ANSI escape sequences, `TIMEOUT` is the 10-second read deadline, `myname` is used in diagnostics, `tty` and `ttyfp` refer to `/dev/tty`, and `tioorig` stores the original terminal attributes for cleanup. The escape templates are `getsize` (`ESC 7`, reset scroll region, move to `999;999`, device status report), `restore` (`ESC 8`), and `size` (`ESC "[%d;%dR"`).

`failed(const char *s)` preserves `errno`, writes a program-name prefix directly to stderr, calls `perror`, and exits. `onintr(int sig)` restores the original termios settings with `tcsetattr(TCSADRAIN)` and exits. `resize_timeout(int sig)` reports a timeout and reuses the interrupt cleanup path. `readstring(FILE *fp, char *buf, const char *str)` arms `SIGALRM`, reads a terminal response until the expected final byte from the format string, normalizes the single-byte CSI value `0233` into `ESC [` when present, and aborts if the first byte does not match the expected response.

`main` owns the full program lifecycle: open `/dev/tty`, put it into noncanonical/no-echo 8-bit mode, query terminal dimensions, restore terminal state, update `struct winsize`, call `ioctl(TIOCSWINSZ)`, and print `COLUMNS`/`LINES`.

## Control Flow

Startup opens `/dev/tty` read/write and records its file descriptor. The program copies current termios settings, disables CR-to-NL translation, disables canonical input and echo, forces `CS8`, and sets `VMIN=6` and `VTIME=1` so escape-response reads have a minimum shape and short inter-byte timeout. It installs `SIGINT`, `SIGQUIT`, and `SIGTERM` handlers only after the original settings are captured.

After switching the terminal into the temporary raw-ish mode, the program writes the size query escape sequence to the terminal. The terminal should save the cursor, reset the scroll region, move to a clamped bottom-right position, and respond to the device-status-report request with `ESC[row;colR`. `readstring` collects that response and `sscanf(buf, size, &rows, &cols)` parses the discovered dimensions. The cursor is restored, the original terminal settings are restored, and signal handlers are reset to default.

The final phase reads the existing kernel window size with `TIOCGWINSZ` when possible. If existing pixel dimensions and row/column counts are available, it scales `ws_xpixel` and `ws_ypixel` proportionally to the newly discovered columns and rows. It then writes the new `ws_row` and `ws_col` via `TIOCSWINSZ`, reports an ioctl error without changing the success exit path, prints the environment assignments, and exits 0.

## State and Persistence Behavior

The only persistent external state mutation is the terminal driver's window-size record for the controlling tty through `TIOCSWINSZ`. The program temporarily mutates terminal line discipline settings but stores `tioorig` and restores it on normal completion, handled signals, and timeout paths. It does not persist files or configuration. Its printed `COLUMNS` and `LINES` values are not applied to the parent shell unless a caller evaluates or otherwise consumes the output.

## Dependencies and Integration Points

The helper depends on a real controlling terminal at `/dev/tty`, ANSI/VT-style escape behavior, POSIX termios, Unix signals and alarms, and `TIOCGWINSZ`/`TIOCSWINSZ` ioctls from `<sys/ioctl.h>`. In xfstests-bld/kvm-xfstests, it integrates with scripts or login/session setup that need terminal dimensions inside VM consoles where inherited window size may be missing or stale.

## Risks and Edge Cases

The program can block until the 10-second alarm if the terminal does not answer the escape query, if stdin/stdout are not connected to an interactive terminal, or if the terminal response is malformed. `readstring` does not check EOF while filling `buf`, and the loop trusts that the expected final byte will eventually appear before the alarm. Signal handling uses functions such as `tcsetattr`, `fprintf`, and `exit` from handlers; this is common in older terminal utilities but not async-signal-safe. `tcsetattr` after entering raw mode is not checked before the query, so write/read failures are diagnosed later and not at the exact failing operation. Pixel scaling uses integer division based on the old row/column counts, so pixel values can lose precision or remain zero.

## Test Signals

Useful signals include compiling the helper on Linux with warnings enabled; running it under a pseudo-terminal that returns a controlled `ESC[24;80R` response and verifying `TIOCSWINSZ` receives 24 rows and 80 columns; timeout testing with a pty that never responds; interruption testing that confirms termios settings are restored after `SIGINT`; and integration testing from a kvm-xfstests console to verify both kernel winsize and emitted `COLUMNS`/`LINES` values match the actual terminal.
