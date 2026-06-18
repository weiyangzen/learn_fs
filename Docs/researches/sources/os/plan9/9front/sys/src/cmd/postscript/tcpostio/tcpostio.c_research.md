# File Research: sources/os/plan9/9front/sys/src/cmd/postscript/tcpostio/tcpostio.c

TCP printer I/O program. It connects to a network PostScript printer, forks into sender and reader halves, uses a socketpair protocol to coordinate status polling and data transmission, sends job data in throttled blocks, and waits for end-of-job/status responses.

Key behavior:
- `parsmesg` recognizes printer status strings inside `%[ ... ]%`.
- `readprinter` repeatedly asks `sendfile` to request status, reads printer/status data, handles timeouts/errors, and commands the sender to send data or stop.
- `sendfile` waits for protocol commands, sends input blocks, sends control-D at start/end, and sends control-T on status requests.
- `main` parses baud-derived block size/debug, dials printer, creates `socketpair`, forks, and combines parent/child exit statuses.

Integration points:
- Uses `dial.c` compatibility function.
- Protocol bytes are single-character constants shared inside the file.

Risks:
- Uses global `fd_set` and timeout structs with `select`; `select` may mutate timeout values on some systems.
- `fprintf(stderr, buf)` treats printer output as a format string, a format-string vulnerability if untrusted printer data is hostile.
- Exit status combines `rprv|sprv`, but `sprv` is a wait status, not just child return code.
