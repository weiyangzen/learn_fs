# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gshsb.h

## Role

`gshsb.h` declares the client-facing HSB color API.

This is color API infrastructure, not filesystem code.

## Public API

- `gs_sethsbcolor(gs_state *, floatp, floatp, floatp)`
- `gs_currenthsbcolor(const gs_state *, float[3])`

The implementation converts through RGB rather than defining an independent device color space.
