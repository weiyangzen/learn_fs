# File Research: sources/os/plan9/9front/sys/src/cmd/audio/mp3enc/brhist.h

This header declares bitrate histogram display support and console I/O state.

Exports:
- `brhist_init()`
- `brhist_disp()`
- `brhist_disp_total()`
- `brhist_jump_back()`
- Global `Console_IO`

Data structures:
- `Console_IO_t` stores reporting streams, optional Windows console handle, display dimensions, terminal-control strings, and a console buffer.

Dependencies and integration:
- Includes `lame.h`.
- Includes `<windows.h>` on Windows non-Cygwin builds.
- Function implementations are outside this group.
- Used by command-line reporting/progress UI rather than core encoding.

Risks:
- Exposes a mutable global `Console_IO`.
- Terminal-control behavior is platform-dependent.
