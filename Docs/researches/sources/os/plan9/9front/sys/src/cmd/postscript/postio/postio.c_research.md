# File Research: sources/os/plan9/9front/sys/src/cmd/postscript/postio/postio.c

`postio.c` is an RS-232/Datakit PostScript printer I/O manager. It sends jobs, watches printer status, logs messages, supports interactive mode, and can split into separate reader/writer processes.

Main flow:
- `main()` initializes signals, parses options, initializes line/buffers, waits for printer readiness, optionally forks, sends input files, waits for job completion, and cleans up.
- `initialize()` reconciles options, allocates the send buffer, initializes message bounds, calls `setupline()`, and saves stdin settings.
- `start()` clears the line and loops until the printer is idle or interactive; it sends ctrl-C/ctrl-D as needed to recover from busy/waiting/error states.
- `split()` optionally forks into read and write processes after `resetline()`.
- `arguments()` sends stdin or each named file.
- `send()` sends buffered blocks while polling/parsing printer status.
- `done()` waits for idle/end-of-job after writes finish.
- `cleanup()` kills the paired writer process if split mode was used.

Status handling:
- Printer messages are expected as `%%[ key: value; ... ]%%`.
- `getstatus()` calls platform `readline()`, logs changed/unknown messages, optionally forwards non-status output to stdout, and sends ctrl-T status requests when appropriate.
- `parsemesg()` tokenizes status/error messages and maps strings through `status[]`.
- Recognized states include busy, waiting, printing, idle, endofjob, printererror, error, flushing, initializing, disconnect, unknown, nostatus, writeprocess, and interactive.

I/O:
- `readblock()` fills `block` from an input fd.
- `writeblock()` writes pending bytes to `ttyo`.
- Wrapper `Read()` and `Write()` respect read/write process roles and tolerate `EINTR`.
- `clearline()` drains status input in single-process mode.
- `slowsend()` can replace normal send if `-S` is selected.

Options:
- Baud, no ctrl-C, interactive, line, quiet, stop bits, data-to-stdout, Datakit window, block size, log file, initial PostScript, one/two process mode, slow send, debug, ignore fatal.

Exit/error behavior:
- `error()` marks exit status and calls `quit()` for fatal/user-fatal unless ignored.
- `interrupt()` handles normal abort signals and the join signal used by split mode.
- `quit()` restores stdin, signals peer, sends printer interrupt/EOF, sleeps briefly, and exits.

Risks:
- Security/robustness is legacy: raw tty control, forking, signal races, global state, old K&R function definitions, and format-string style logging through trusted internal strings.
- Status parsing is heuristic and comments acknowledge incomplete correctness.
- Split-mode behavior depends heavily on platform `resetline()`.
- `getbaud()` has no return after fatal error in source form, relying on `error(FATAL)` exit behavior.

Filesystem relevance: it opens job files and device paths, but its substantive role is printer line management rather than filesystem logic.
