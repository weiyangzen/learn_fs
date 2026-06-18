# File Research: sources/os/bsd/dragonflybsd/sys/sys/serial.h

This header defines serial-port modem signal bits, delta bits, and kernel interrupt-source bits independent of tty processing.

Key responsibilities:
- Defines modem/control state bits:
  - `SER_DTR`, `SER_RTS`, `SER_STX`, `SER_SRX`
  - `SER_CTS`, `SER_DCD`, `SER_RI`, `SER_DSR`
- Defines `SER_MASK_STATE`.
- Defines `SER_DELTA(x)` and per-signal delta bits such as `SER_DDTR`, `SER_DCTS`, and `SER_DDSR`.
- Defines `SER_MASK_DELTA`.
- In kernel builds, defines interrupt-source flags:
  - `SER_INT_OVERRUN`
  - `SER_INT_BREAK`
  - `SER_INT_RXREADY`
  - `SER_INT_SIGCHG`
  - `SER_INT_TXIDLE`
- Defines interrupt masks:
  - `SER_INT_MASK`
  - `SER_INT_SIGMASK`
- Defines kernel interrupt callback type `serdev_intr_t`.

Important invariants:
- Modem bits are intended to match shifted `TIOCMGET` definitions from `<sys/ttycom.h>`.
- Both state and delta bits must fit in 16 bits.
- Kernel interrupt bits intentionally use upper bits so lower 16 bits remain for signal state/delta.

Research notes:
- This is a small cross-driver serial signal vocabulary, not a full serial driver interface.
