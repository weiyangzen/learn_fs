# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/istream.h

Purpose: declares interpreter-level stream support routines exported by `zfproc.c`.

APIs:
- `sread_proc` and `swrite_proc` initialize procedure-backed streams for filters.
- `s_handle_read_exception` and `s_handle_write_exception` integrate stream interrupts/callouts with interpreter execution-stack continuations.

This header is the bridge between the stream package and interpreter continuation handling used by scanners, file IO, filters, and painting code.
