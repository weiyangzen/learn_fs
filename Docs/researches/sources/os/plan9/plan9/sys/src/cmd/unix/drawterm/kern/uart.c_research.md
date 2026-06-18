# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/kern/uart.c

This file is a UART output stub.

Key behavior:
- `uartputs` writes bytes to host file descriptor 2 unless `panicking` is set.

Important details:
- This gives hosted kernel code a serial-console-like diagnostic sink.
