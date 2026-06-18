# File Research: sources/os/plan9/plan9/sys/src/9/ppc/uartsmc.h

Shared data declaration for MPC8260 SMC UART state.

Key contents:
- Defines `UartData` fields for SMC number, SMC registers, SMC parameter RAM, RX/TX buffers, RX/TX BDs, and init/enable state.
- Declares `uartdata[Nuart]`, `baudgen`, and `smcsetup`.

Role:
- Lets board-specific and UART code share SMC UART state and setup entry points.

Notable risks:
- The header defines storage, not just extern declarations, so including it in multiple C translation units would duplicate `uartdata`.
