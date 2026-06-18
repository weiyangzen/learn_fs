# File Research: sources/os/plan9/plan9/sys/src/9/ppc/msaturn.h

Small Saturn board interrupt-vector header.

Key contents:
- Defines `Vecuart0`, `Vecuart1`, `Vectimer0`, `Vecether`, and `Vecunused`.

Role:
- Shared by Saturn interrupt, UART, timer, and Ethernet code to agree on logical interrupt vector numbers.

Notable risks:
- Constants are tightly tied to `msaturn.c` priority table.
