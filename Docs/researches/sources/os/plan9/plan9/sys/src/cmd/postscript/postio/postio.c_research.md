# File Research: sources/os/plan9/plan9/sys/src/cmd/postscript/postio/postio.c

Serial/Datakit I/O manager for PostScript printers.

Key responsibilities:
- Opens/configures the printer line, verifies printer readiness, sends PostScript jobs, monitors printer status, and waits for completion.
- Supports single-process mode and optional split read/write processes.
- Supports interactive mode, quiet mode, slow-send fallback, page/job data returned to stdout, printer log files, custom initial PostScript, baud/stop-bit settings, and Datakit window size.
- Parses printer status/error messages like `%%[ status: idle ]%%`, `%%[ Error: ... ]%%`, and `%%[ PrinterError: ... ]%%`.
- Handles signal cleanup, printer reset/EOF, child process termination, and terminal restoration.

Control flow:
- `main()` calls signal setup, option parsing, initialization, printer startup, optional process split, input argument sending, completion wait, and cleanup.
- `initialize()` resolves mode interactions, allocates the send buffer, initializes message bounds, calls platform `setupline()`, and saves stdin terminal state.
- `start()` clears stale line data and polls status until the printer is idle/interactive, sending control-C or EOF when needed.
- `split()` forks into read and write processes when requested and supported by platform `resetline()`.
- `arguments()` sends stdin or each named input file when the current process can write.
- `send()` reads file blocks and writes them based on current printer state; it aborts on PostScript errors, flushing, or disconnects.
- `done()` waits for end-of-job or idle state after writing, coordinating split reader/writer completion through `joinsig`.
- `cleanup()` kills and waits for the peer process in split mode.

Status and parsing:
- `getstatus()` reads a complete line using platform `readline()`, parses it, logs state changes, optionally forwards non-status output to stdout, or sends control-T status queries.
- `parsemesg()` extracts bracketed printer reports, tokenizes key/value pairs, recognizes status/error keywords through `STATUS`, and maps Datakit conversation end to `DISCONNECT`.
- `find()` is a local substring search returning the match or string end.

I/O helpers:
- `readblock()` fills `block` from input and optionally logs fake busy status in quiet mode.
- `writeblock()` writes pending bytes from `block` to `ttyo`.
- `Read()` and `Write()` wrap system calls so split read-only/write-only processes can share code.
- `Rest()` suppresses sleeps in read-only processes.
- `clearline()` drains printer input only in single-process mode.

Error/signal handling:
- `interrupt()` handles normal termination signals and the split-process join signal.
- `error()` logs messages, sets `x_stat`, and exits via `quit()` for fatal errors unless `ignore` is enabled.
- `quit()` signals the peer, restores stdin, sends printer interrupt/EOF when connected, waits briefly, and exits.

Dependencies:
- Platform line operations from `ifdef.c`.
- Constants and lookup tables from `postio.h`.
- Shared `gen.h` booleans/error constants.
- Optional `slowsend()` from `slowsend.c`.

Risks and quirks:
- Heavy global mutable state couples process role, current printer state, buffers, message parsing, and signal cleanup.
- Split-process coordination is signal-based and timing-sensitive.
- `parsemesg()` uses `strtok()` and simplified parsing; unusual status values with embedded delimiters may be misclassified.
- The `getbaud()` fatal path has no explicit return after `error()`, relying on `error()` exit behavior.
- `Write()` treats `EINTR` as a successful full write, which can hide interrupted writes in some paths.
