# File Research: sources/os/plan9/plan9/sys/src/cmd/postscript/postio/ifdef.c

System-dependent serial-line, terminal, and Datakit support for `postio`.

Key responsibilities:
- Provides conditional implementations of:
  - `setupline()`
  - `resetline()`
  - `setupstdin()`
  - `readline()`
- Supports `SYSV`, `V9`, and `BSD4_2` terminal APIs.
- Supports optional `DKHOST` Datakit connection setup.
- Supplies fallback `strspn()`, `strpbrk()`, and `strtok()` for BSD builds.
- Manages terminal modes for raw/interactive input and split reader/writer processes.

System V path:
- Opens a tty or optional DKHOST destination, duplicates input/output descriptors, enables nonblocking reads, sets termio flags, configures baud/stop bits, flushes the line, and wraps `ttyi` in `fp_ttyi`.
- `resetline()` disables nonblocking mode, enables XON/XOFF flow control, and makes reads blocking for split-process mode.
- `setupstdin()` saves/restores stdin termio and sets noncanonical no-echo mode for interactive mode.
- `readline()` reads one byte at a time, assembles complete printer status lines in `mesg`, synthesizes `endofjob` on control-D, and has a split-reader workaround for repeated zero-length reads.

V9 path:
- Includes `<ipc.h>` and can open either local device paths or Datakit IPC paths.
- Pushes a tty line discipline, configures `ttydevb` speeds and `sgttyb` flags, disables echo/CRMOD, and sets CBREAK.
- `readline()` uses `FIONREAD` and an internal `tbuf` buffer for efficiency, with different behavior for interactive mode and split read/write mode.

BSD4_2 path:
- Uses `sgtty`, `TIOCSETD`, `TIOCLGET`, `LDECCTQ`, `CBREAK`, and `TANDEM`.
- Provides similar stdin setup and line-reading semantics.
- Defines local string tokenization helpers for older libc environments.

DKHOST path:
- `dkhost_connect()` dials a Datakit destination, temporarily redirects `stderr` to the printer log during dialing, handles retry backoff, configures Datakit read mode/window parameters when available, maps to a tty name, and opens it for normal I/O.

Dependencies:
- Uses globals declared in `ifdef.h` and defined in `postio.c`: `line`, `ttyi`, `ttyo`, `fp_log`, `mesg`, `endmesg`, `baudrate`, `stopbits`, `interactive`, `whatami`, `canread`, `canwrite`.
- Uses shared `gen.h` error constants and `error()`.

Risks and quirks:
- Large portions are platform-specific legacy tty code and comments note some V9/BSD split-process paths were not tested.
- System V split-reader zero-read handling is explicitly a workaround for printer-offline hangs.
- Some APIs and constants are obsolete outside their target systems.
- DKHOST support changes `line` after connecting and depends on external Datakit library behavior.
