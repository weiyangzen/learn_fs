# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ser_sync.h

## Role

Defines synchronous serial line ioctls, mode/status/statistics structures, and private STREAMS state for sync serial drivers.

## Key Interfaces

- Ioctls cover get/set SCC mode, statistics, speed, MRU/MTU, modem control, and DTR.
- `struct scc_mode` carries transmit/receive clock source, inversion flags, connection config, baud rate, and validation error mask.
- Clock constants describe external clocks, baud generators, PLL, system clock, and inversion modes.
- Connection flags cover half duplex, multipoint, IBM-SDLC, modem-signal reporting, NRZI, loopback, and echo.
- `struct sl_status` reports modem/link events with timestamp; `sl_status32` is syscall32-compatible.
- `struct sl_stats` counts packets, bytes, aborts, CRCs, CTS/DCD events, underrun/overrun, and buffer failures.
- `struct ser_str` and `struct syncline` describe per-stream and protocol private driver state.

## State Flags

Defines transmit-state bits (`TX_IDLE`, `TX_ACTIVE`, `TX_ABORTED`, etc.), link flags (`SF_FDXPTP`, `SF_LINKERR`, etc.), clone-open state, and watchdog timing macros.

## Risk Notes

This header mixes ioctl ABI with driver-private STREAMS layout. Ioctl values/status constants are externally visible, while private fields must match driver implementation assumptions.
