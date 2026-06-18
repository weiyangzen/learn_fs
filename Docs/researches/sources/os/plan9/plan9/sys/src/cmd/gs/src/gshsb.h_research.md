# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gshsb.h

## Role

Client interface for HSB color routines.

## Main API

Declares `gs_sethsbcolor(gs_state *, floatp, floatp, floatp)` and `gs_currenthsbcolor(const gs_state *, float[3])`.

## Dependencies

Requires Ghostscript graphics state and floating-point typedefs from surrounding includes.

## Notes

The implementation maps HSB through RGB; no independent HSB color space state is stored here.
