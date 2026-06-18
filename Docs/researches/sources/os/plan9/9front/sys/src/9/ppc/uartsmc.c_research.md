# File Research: sources/os/plan9/9front/sys/src/9/ppc/uartsmc.c

Implements a PPC 8260 SMC UART driver using CPM-style buffer descriptors. It configures SMC UART mode, allocates RX/TX descriptors and cacheline-aligned buffers, programs baud generators, and exposes `smcphysuart`.

Key paths: `smcinit` performs hardware setup via `smcsetup`, configures descriptors, events, and `smcmr`; `smcenable` enables SMC interrupts; `smcinterrupt` handles break, busy/error, receive buffer, and transmit buffer events. `smckick` writes staged output into the TX buffer descriptor and flushes cache before marking it `BDReady`.

Dependencies include PPC CPM structures from `imm.h` and `uartsmc.h`, `bdalloc`, `dcflush`, `dczap`, `sync`, and `intrenable`. Only SMC1 is active; SMC2 is present but commented out.
