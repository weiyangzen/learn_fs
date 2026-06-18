# File Research: sources/os/plan9/plan9/sys/src/cmd/fossil/9proc.c

Connection and 9P message dispatcher for fossil.

It maintains pooled `Con` and `Msg` objects, starts per-connection read/write threads, queues incoming 9P messages to worker threads, dispatches through `rFcall`, and serializes replies. `Tflush` handling is careful: requests that have not begun processing can be marked flushed, flush requests are chained to the original message, and replies are ordered so a flush response follows the disposition of the flushed request.

The file also implements console commands `msg`, `con`, and `who` for tuning pool sizes and inspecting active connections/fids. It depends heavily on Plan 9 threading primitives, `read9pmsg`, `convM2S`/`convS2M`, and fossil's `Con`, `Msg`, and `Fid` structures from `9.h`.
