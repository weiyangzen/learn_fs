# File Research: sources/os/plan9/plan9/sys/src/9/ppc/uartsmc.c

MPC8260 SMC UART driver implementing Plan 9 `PhysUart` for SMC1.

Key responsibilities:
- Defines SMC mode/event bits, BD error bits, and 32-byte RX/TX buffer sizing.
- Creates `SMC1` UART config and PNP list.
- `smcsetup` configures SMC parameter RAM, Port D pins, BRG, clock mux, and CPM init command.
- `smcinit` allocates receive/transmit BDs and buffers, initializes parameter RAM, clears events, and programs UART mode.
- Provides enable/disable, status, FIFO/no-op modem control, parity/stop/bits/baud changes, break stub, TX kick, interrupt RX/TX handling, polled getc/putc, and console selection.

Important behavior:
- SMC BDs must be allocated from dual-port RAM via `bdalloc`.
- RX interrupt invalidates data cache before copying received bytes.
- TX flushes cache before handing the descriptor to CPM.
- Only SMC1 is configured; SMC2 config is commented out.

Dependencies:
- Depends on MPC8260 `imm.h`/`m8260.h`, CPM command helpers, I/O locking, UART framework, and board interrupt vector constants.

Notable risks:
- `smcstatus` repeats the Saturn stack-buffer/free bug.
- Some mode setters disable RX/TX but do not explicitly restore enable bits in all cases.
- Polled getc/putc paths spin on descriptor ownership.
