# File Research: sources/os/plan9/9front/sys/src/cmd/postscript/postio/ifdef.c

`ifdef.c` contains the platform-dependent tty, Datakit, stdin, and line-reading code used by `postio.c`.

Structure:
- Conditional sections for `SYSV`, `V9`, `BSD4_2`, and `DKHOST`.
- Each platform provides `setupline()`, `resetline()`, `setupstdin(mode)`, and `readline()`.
- Shared globals are declared through `ifdef.h` and defined mostly in `postio.c`.

System V path:
- Opens a supplied tty line or uses stdout’s descriptor if no line is supplied.
- Optional DKHOST connection support.
- Configures termio flags, baud, stop bits, raw-ish mode, no-delay reads, and flow control.
- `resetline()` disables no-delay and enables IXON/IXOFF for split reader/writer mode.
- `setupstdin()` saves/restores stdin and sets noncanonical/no-echo interactive mode.
- `readline()` reads status lines one byte at a time, converts control-D to synthetic `endofjob`, and includes a two-process offline kludge after repeated zero-length reads.

V9 path:
- Supports local device opens and Datakit-style `ipcopen(ipcpath(...))`.
- Pushes tty line discipline, configures ttydev speed, CBREAK, and special chars.
- `resetline()` enables tandem flow control.
- `readline()` uses `FIONREAD` into a temporary buffer and has an interactive pass-through loop.

BSD 4.2 path:
- Configures NTTY discipline, CBREAK, speeds, DEC-style flow control, and special chars.
- Provides local fallback implementations of `strspn`, `strpbrk`, and `strtok`.
- `readline()` uses `FIONREAD` and `getc(fp_ttyi)`.

DKHOST path:
- `dkhost_connect()` dials Datakit destinations, temporarily redirects `stderr` to the printer log for dial errors, optionally configures receive mode/window size, maps the Datakit minor to a device name, and reopens it.

Risks:
- Heavy conditional compilation with unprototyped old C.
- Platform branches are explicitly described as untested in places.
- Fixed-size `mesg` handling is bounded by `endmesg`, but line truncation is possible.
- Uses legacy tty/ioctl APIs and Datakit interfaces.

Filesystem relevance: indirect OS/tty interaction only; no filesystem implementation.
