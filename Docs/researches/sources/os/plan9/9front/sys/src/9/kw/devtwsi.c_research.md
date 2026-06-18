# File Research: sources/os/plan9/9front/sys/src/9/kw/devtwsi.c

Implements the Kirkwood TWSI/I2C device.

Key elements:
- Defines TWSI register layout, control bits, and status codes.
- Uses a single global transfer state protected by `QLock`.
- Implements interrupt-driven read and write state machines.
- Starts transfers by setting `Twsistart`, waits for interrupts, advances by status code, and finishes with STOP.
- Exposes `#²/twsi`; read/write offsets are interpreted as device addresses.
- Registers and unregisters the TWSI interrupt handler during device init/shutdown.

Dependencies:
- Uses `soc.twsi`, Kirkwood interrupt constants, Plan 9 device framework, rendezvous sleep/wakeup, and coherence barriers.

Research notes:
- The driver supports one active transfer at a time.
- Abnormal status codes terminate the transfer and raise an error.
