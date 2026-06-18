# File Research: sources/os/plan9/9front/sys/src/9/pc/archmp.c

Intel MultiProcessor Specification table parser and MP-mode PC architecture backend.

Key responsibilities:
- Locates `_MP_` floating pointer and maps/checks the referenced `PCMP` configuration table.
- Builds processor APIC, bus, I/O APIC, I/O interrupt, and local interrupt structures from PCMP entries.
- Initializes local/I/O APICs and starts application processors through `mpinit()`.
- Provides MP reset by shutting down application processors and delegating to generic reset.
- Supports boot-time `*mp` table override and `*dumpmp` hex dump diagnostics.

Important behavior:
- Rejects MP default configurations and accepts PCMP versions 1 and 4 only.
- Assigns boot processor mach number 0 and increments application processor mach numbers from 1.
- Uses bus defaults for ISA/EISA/PCI polarity and trigger mode.
- Contains a board-specific workaround for an Intel SR1520ML interrupt-routing bug.
- Selects TSC fast clock when available and not disabled by `*notsc`.

Dependencies:
- Depends on MP table structures from `mp.h`, APIC setup, PCI, `sigsearch`, `vmap`, `memreserve`, and generic i8259 IRQ-number compatibility.

Notable risks:
- PCMP entry parsing assumes table entries are ordered sufficiently for one pass.
- Destination I/O APIC value `0xff` for I/O interrupts is treated as unsupported.
