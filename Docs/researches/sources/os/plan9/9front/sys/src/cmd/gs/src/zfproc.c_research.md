# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/zfproc.c

## Purpose
Implements procedure-backed stream support, allowing PostScript procedures to serve as filter sources or sinks and to resume I/O after callouts.

## Key Functions
- `s_proc_init()` allocates a stream and `stream_proc_state` for read or write procedure streams.
- `sread_proc()` creates a procedure read stream.
- `s_proc_read_process()` copies data returned by the procedure into the read buffer or requests `CALLC`.
- `s_handle_read_exception()` builds e-stack continuation frames for read interruptions/callouts and stdin callouts.
- `s_proc_read_continue()` consumes the procedure's returned string and resumes reading.
- `swrite_proc()` creates a procedure write stream.
- `s_proc_write_process()` copies buffered output into the string supplied by the procedure or requests `CALLC`.
- `s_proc_write_flush()` flushes buffered output through procedure callback semantics.
- `s_handle_write_exception()` builds write continuation frames and stdout/stderr callouts.
- `s_proc_write_continue()` installs a new writable buffer string after a callback.
- `s_is_proc()` identifies procedure-backed streams.

## Important Behavior
- Procedure stream state contains PostScript refs (`proc`, `data`) and has custom GC mark/relocate procedures.
- `CALLC` asks the interpreter to execute the stored procedure; `INTC` pushes an interrupt continuation.
- Stdin/stdout/stderr streams add `.needstdin`, `.needstdout`, or `.needstderr` callouts so the outer interpreter caller can provide data or consume output.
- Read procedures return strings; zero-length strings mark EOF.
- Write procedures receive a data string and a boolean indicating whether more data follows.

## Research Notes
This is the continuation engine behind procedure filters and the exceptional stream statuses handled in `zfileio.c`.
