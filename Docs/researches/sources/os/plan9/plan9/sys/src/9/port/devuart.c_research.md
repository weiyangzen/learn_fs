# File Research: sources/os/plan9/plan9/sys/src/9/port/devuart.c

Purpose: Generic UART device `#t` for serial ports discovered by architecture-specific `PhysUart` drivers. It exposes `eiaN`, `eiaNctl`, and `eiaNstatus` files for each port.

Key logic:
- `uartreset` calls each `physuart[i]->pnp`, builds a flat UART list and directory table, enables console/special ports, and starts a periodic staging timer.
- `uartenable` opens input/output queues, initializes staging buffers, default line settings, physical hardware, and enabled-list membership.
- `uartopen` enables ports on first data/control open; `uartclose` drains output, closes queues, disables hardware, and clears hangup flags on final close.
- `uartread` returns queued input, port number, or physical status.
- `uartwrite` sends data to the output queue or parses control commands.
- `uartctl` supports baud, bits, stop bits, parity, break, DTR/RTS, modem control, FIFO, queue limits, nonblocking output, hangup, flush, timer period, and software flow control.
- Interrupt-time helpers `uartrecv`, `uartkick`, and `uartstageoutput` bridge physical UART drivers with generic queues.
- `uartclock` batches staged input, handles hangups, and restarts output after flow-control backoff.

Dependencies and integration:
- Depends on generated `physuart[]`, `PhysUart` methods, `Queue`, `Timer`, console globals (`kbdq`, `serialoq`, `consuart`), and Plan 9 device helpers.

Risks and notes:
- Input staging is intentionally timer-flushed to reduce per-character interrupt overhead.
- Output draining before line-setting changes can sleep and is used broadly in `uartctl`.
- Software XON/XOFF and hardware backoff interact through `blocked`, `cts`, and `ctsbackoff`.
