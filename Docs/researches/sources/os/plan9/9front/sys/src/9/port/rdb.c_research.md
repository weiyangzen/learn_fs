# File Research: sources/os/plan9/9front/sys/src/9/port/rdb.c

Minimal serial remote debugger loop.

Key responsibilities:
- Reads line commands from `uartgetc()`.
- Supports `r<addr>` to read four bytes and `w<addr> <value>` to write a 32-bit value.
- Treats small addresses as offsets into the supplied `Ureg`, otherwise as raw virtual addresses.
- Resets console UART state for debugger use and disables serial output queues.
- Enters debugger with interrupts high through `rdb()` and `callwithureg()`.

Important behavior:
- Drops `/dev/kprint` by clearing `kprintoq`.
- Runs an infinite command loop once entered.

Notable risks:
- It performs unchecked raw memory reads/writes from debugger input.
- Intended for emergency/debug use, not normal safe operation.
