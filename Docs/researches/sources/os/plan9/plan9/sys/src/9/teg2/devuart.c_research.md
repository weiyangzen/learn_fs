# File Research: sources/os/plan9/plan9/sys/src/9/teg2/devuart.c

Generic Plan 9 UART device (`#t`) for Tegra, implementing queue management, file namespace, control parsing, flow control, staging, and console fallbacks over physical UART drivers.

Key responsibilities:
- Discovers UARTs through registered `PhysUart` providers and builds `eiaN`, `eiaNctl`, and `eiaNstatus` directory entries.
- Enables/disables UARTs, opens/closes input/output queues, maintains a list of active UARTs, and starts a periodic service timer.
- Parses UART control commands for baud, bits, stop, parity, FIFO, modem, DTR/RTS, hangup, flush, break, queue limits, nonblocking mode, timer period, and software flow control.
- Stages output from queues into fixed buffers and calls physical `kick`.
- Stages interrupt-time input into rings and periodically moves it to queues.
- Handles XON/XOFF, CTS backoff, hangup, mouse/special UART hooks, and console `uartgetc`/`uartputc`/`uartputs`.

Important behavior:
- `uartenable` returns early if `up` is nil, allowing early boot to retry later.
- Console UARTs bind their input/output queues to `kbdq` and `serialoq` and use `kbdcr2nl`.
- `uartclock` both drains input staging and periodically kicks output to avoid stalls.

Dependencies and assumptions:
- Depends on `PhysUart` implementations, Plan 9 queues, `addclock0link`, and `netif` QID macros.
- The active UART list is protected with interrupt locks because timer callbacks can run during device operations.

Notable risks:
- UART close drains output with sleep and hangup semantics; physical drivers must implement `kick`/status correctly.
- Staging rings can overflow; `uartstageinput` records queue errors and may deassert RTS.
