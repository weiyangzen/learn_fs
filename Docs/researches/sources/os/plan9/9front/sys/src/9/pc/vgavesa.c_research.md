# File Research: sources/os/plan9/9front/sys/src/9/pc/vgavesa.c

VESA BIOS Extensions framebuffer support for the PC kernel VGA layer. It uses `/dev/realmode` and `/dev/realmodemem` to call VBE interrupt `0x10`, validates the current VBE mode, derives framebuffer geometry, and registers a linear framebuffer mapping.

Key behavior:
- Defines a 32-bit real-mode `Ureg386` interface and a shared mode-info buffer at `RealModeBuf`.
- `vbesetup` prepares BIOS register state and clears the mode buffer.
- `vbecall` copies mode buffer state into real-mode memory, invokes interrupt `0x10`, checks VBE success status, and reads the mode buffer back.
- `vbecheck`, `vbegetmode`, and `vbemodeinfo` validate VBE 2+ support and fetch the active mode’s mode-info block.
- `vmode` decodes VBE attributes, bytes-per-line, dimensions, depth, physical framebuffer address, and Plan 9 channel string.
- `vesalinear` maps the current linear framebuffer, using PCI BAR containment when possible to size the mapping and falling back to a heuristic if PCI sizing is unavailable.
- `vesablank` uses VBE DPMS function `0x4f10`, with a process alarm guard for kernel processes because some BIOS implementations can hang in blank/unblank calls.
- `vesabootscreenconf` converts bootloader-provided VBE mode info into a `*bootscreen=` configuration line.

Notable dependencies:
- Plan 9 real-mode devices, channel I/O, and error unwinding.
- VGA linear mapping helpers `vgalinearaddr` and `addvgaseg`.
- PCI scanning for framebuffer BAR sizing.

Research notes:
- This driver relies on the BIOS mode already being set; it does not enumerate or select modes.
- The Bochs note explains why the current mode’s linear bit is not trusted strictly.
- The static `creg` and `cmem` channels are global driver state, opened on enable and closed on disable.
