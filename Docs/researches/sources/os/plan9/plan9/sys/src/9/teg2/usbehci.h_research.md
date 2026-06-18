# File Research: sources/os/plan9/plan9/sys/src/9/teg2/usbehci.h

Local EHCI USB controller definitions for the Tegra2 port.

Key contents:
- Overrides debug macros from the generic USB code.
- Forward-declares EHCI private types.
- Defines `Poll`, `Ctlr`, and operational register structure `Eopio`.
- Declares EHCI linkage and memory/run helpers.

Notes:
- `Ctlr` captures async/periodic queue state, frame list, interrupt counters, and polling rendezvous.
- `Eopio` includes standard EHCI operational registers plus implementation-specific `insn` registers.
