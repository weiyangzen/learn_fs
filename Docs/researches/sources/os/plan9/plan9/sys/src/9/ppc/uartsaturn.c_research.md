# File Research: sources/os/plan9/plan9/sys/src/9/ppc/uartsaturn.c

Saturn dual-UART driver implementing Plan 9 `PhysUart` operations and console/debug output.

Key responsibilities:
- Defines Saturn UART register layout, bit encodings, two UART instances, and default UART configs.
- Provides PNP list, init/enable/disable, status, parity/stop/bits/baud changes, interrupt handling, polled getc/putc, and transmitter kick.
- Handles RX full, TX empty, and RX error interrupts.
- Selects console UART from `console=` config.
- Provides low-level `dbgputc`, `dbgputs`, and `dbgputx` on UART A.

Important behavior:
- Baud divisor uses `14745600/16`.
- `sukick` sends staged output when TX interrupt reports empty.
- `sugetc` uses a static buffered polled read path.
- `suinterrupt` explicitly calls `intack`.

Dependencies:
- Depends on `msaturn.h`, generic UART layer functions, and Saturn interrupt controller.

Notable risks:
- `sustatus` uses a stack buffer but calls `free(p)`, which is erroneous.
- `suenable` range check permits `nr == Nuart`, which is out of bounds.
- Busy-wait get/put paths can spin forever if hardware is unresponsive.
