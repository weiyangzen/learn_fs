# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsnogc.h

Interface for the non-tracing GC/reclaim procedure.

Key declaration:
- `extern vm_reclaim_proc(gs_nogc_reclaim);`

Dependencies:
- Includes `gsgc.h` for `vm_reclaim_proc`.

Research notes:
- This header exposes `gs_nogc_reclaim` to VM/allocator code that expects a reclaim callback.
