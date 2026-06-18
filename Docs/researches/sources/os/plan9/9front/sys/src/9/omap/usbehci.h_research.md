# File Research: sources/os/plan9/9front/sys/src/9/omap/usbehci.h

EHCI host-controller structures and constants used by OMAP USB code.

Key contents:
- Debug-print macros controlled by `ehcidebug`.
- Forward declarations and incomplete pragmas for EHCI controller structures.
- EHCI capability, command, status, interrupt, config, port, and debug-port bit constants.
- `Poll`, `Ctlr`, `Eopio`, and `Ecapio` structure definitions for generic EHCI controller state and MMIO registers.
- OMAP UHH register layout and hostconfig bit definitions.
- Declarations for generic EHCI linkage/memory/run helpers.
- `dmaflush` macro is empty for this port.

Research notes:
- This header bridges OMAP-specific controller setup in `usbehciomap.c` with generic EHCI logic elsewhere in the 9front tree.
