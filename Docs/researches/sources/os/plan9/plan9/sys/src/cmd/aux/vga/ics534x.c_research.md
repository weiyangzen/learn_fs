# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/vga/ics534x.c

ICS534x GENDAC backend, assumed wired to ET4000-W32p or ARK2000PV boards.

Core behavior:
- Uses controller-specific RS2 routing:
  - ET4000-W32 via CRTC `0x31`.
  - ARK2000PV via sequencer `0x1C`.
- Advertises `Hpclk2x8`.
- Parses speed grade suffix, default 80 MHz.
- Optionally halves requested clock and enables 2x8-bit mode when supported and beneficial.
- Computes PLL parameters `M/N/R` under documented constraints.
- Programs PLL entry `f7`, PLL control register, and pixel mode through DAC registers.
- Dumps all PLL frequency entries and command/control registers.

Ctlr:
- `ics534x`

Notable risks:
- Errors if used with an unsupported main controller.
- Assumes ICS534x clock select and RS2 wiring match one of the two coded board families.
