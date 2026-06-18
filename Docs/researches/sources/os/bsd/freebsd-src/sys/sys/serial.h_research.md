# File Research: sources/os/bsd/freebsd-src/sys/sys/serial.h

Common serial-port signal and interrupt bit definitions.

Key responsibilities:
- Defines modem control signal bits: `SER_DTR`, `SER_RTS`, `SER_CTS`, `SER_DCD`, `SER_RI`, `SER_DSR`, and related secondary TX/RX bits.
- Defines delta-bit encoding through `SER_DELTA()` and delta masks such as `SER_DCTS`.
- Under kernel visibility, defines common serial interrupt source bits for overrun, break, RX-ready, signal-change, and TX-idle.
- Defines `serdev_intr_t` callback type for serial interrupt handlers.

Important patterns:
- Modem signal bits intentionally match shifted `TIOCMGET` definitions, with consistency asserted elsewhere.
- Low 16 bits are reserved for state/delta signals; high bits describe interrupt sources.

Research relevance:
- Device-driver ABI helper for serial hardware and umbrella serial controller drivers.
