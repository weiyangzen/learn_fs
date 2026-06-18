# File Research: sources/os/plan9/9front/sys/src/9/pc/devlpt.c

Centronics parallel printer-port device implementing `#L`.

Key responsibilities:
- Supports classic LPT base addresses `0x378`, `0x3bc`, and `0x278`.
- Exposes per-port files for data latch, printer status, printer control, and byte-stream data output.
- Allocates I/O port ranges on attach and detects ECP extended-control register mode when present.
- Writes raw register values or sends bytes with strobe/ready handshaking.
- Handles printer interrupts by waking blocked writers.

Important behavior:
- Attach spec selects 1-based LPT number, defaulting to LPT1.
- `data` writes loop one byte at a time through `outch()`.
- `outch()` waits for not-busy, checks paper/select/error bits, enables interrupts while sleeping, then strobes data.

Dependencies:
- Depends on I/O allocation, parallel-port IRQ, device framework, and low-level port I/O.

Notable risks:
- The initial one-time interrupt disable uses `lptbase[i-1]` before range validation of `i`.
- Error handling resets control register to `Finitbar` on write failure.
