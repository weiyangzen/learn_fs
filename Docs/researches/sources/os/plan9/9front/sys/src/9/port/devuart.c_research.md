# File Research: sources/os/plan9/9front/sys/src/9/port/devuart.c

Implements the `#t` UART device. It enumerates physical UART providers from `physuart[]`, builds `eiaN`, `eiaNctl`, and `eiaNstatus` entries, and exposes serial input/output through Plan 9 queues.

`uartenable` opens input/output queues, applies default line settings, enables the physical UART, and links it into the enabled UART list. `uartdisable` removes it and calls the hardware disable hook. `uartopen` increments open counts for control/data files; `uartclose` closes queues, drains output, disables hardware, and clears modem hangup state.

Control commands in `uartctl` configure baud, DTR/RTS, FIFO, break, bits, parity, stop bits, queue limits, nonblocking mode, timer cadence, modem control, hangup behavior, and software flow control. RX interrupt input enters an interrupt staging ring via `uartrecv`, then `uartclock` periodically flushes it to the input queue and handles hangups/backoff.

The file also owns console UART helpers `uartgetc`, `uartputc`, and `uartputs`, plus mouse-special UART entry points. Main dependencies are `PhysUart`, `Uart`, queues, timers, and `netif` qid encoding.
