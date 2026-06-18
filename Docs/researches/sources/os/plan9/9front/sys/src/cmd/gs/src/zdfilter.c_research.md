# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/zdfilter.c

Provides PostScript access to the device filter stack.

Key behavior:
- Defines `.popdevicefilter`.
- Calls `gs_pop_device_filter` using stable interpreter memory and the current graphics state.
- Notes that `pushpdf14devicefilter` is defined elsewhere.

Dependencies:
- Uses graphics-state/device-filter APIs from `gsdfilt.h`.

Research notes:
- This is a minimal operator wrapper. Its main role is exposing device-filter unwinding to PostScript-level transparency/filter management.
