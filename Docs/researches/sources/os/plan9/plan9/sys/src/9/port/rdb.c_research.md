# File Research: sources/os/plan9/plan9/sys/src/9/port/rdb.c

Implements a minimal serial remote debugger.

Behavior:
- `rdb` raises interrupt priority, prints `rdb...`, and calls `talkrdb` with a captured `Ureg`.
- `talkrdb` disables serial console output queues, prints `Edebugger reset`, then reads line-oriented commands from `uartgetc`.
- Command `r<hexaddr>` reads 4 bytes at an address and replies with `R<addr> <b0> <b1> <b2> <b3>`.
- Command `w<hexaddr> <hexvalue>` writes a word and replies `W`.
- Addresses below `sizeof(Ureg)` are interpreted as offsets into the saved register frame; otherwise as absolute addresses.
- Unknown commands return `Eunknown message`.

Role:
- Tiny low-level debugging endpoint for memory/register inspection and modification over UART.
