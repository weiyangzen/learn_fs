# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/zfproc.c

## Purpose
Implements procedure-backed stream support, allowing PostScript procedures to serve as filter sources or sinks and to resume I/O after callouts.

## Key Functions
- `s_proc_init()` allocates a stream and `stream_proc_state`.
- `sread_proc()` and `swrite_proc()` create procedure read/write streams.
- `s_proc_read_process()` and `s_proc_write_process()` move data between stream buffers and procedure-provided strings.
- `s_handle_read_exception()` and `s_handle_write_exception()` build e-stack continuation frames.
- `s_proc_read_continue()` and `s_proc_write_continue()` resume after callbacks.
- `s_is_proc()` identifies procedure-backed streams.

## Important Behavior
- Procedure stream state contains PostScript refs and has custom GC mark/relocate procedures.
- `CALLC` asks the interpreter to execute the stored procedure; `INTC` pushes an interrupt continuation.
- Stdin/stdout/stderr streams add `.needstdin`, `.needstdout`, or `.needstderr` callouts.
- Read procedures return strings; zero-length strings mark EOF.

## Research Notes
Continuation engine behind procedure filters and stream statuses handled in `zfileio.c`.
