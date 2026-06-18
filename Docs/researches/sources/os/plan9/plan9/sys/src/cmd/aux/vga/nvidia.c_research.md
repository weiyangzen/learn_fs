# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/vga/nvidia.c

Implements `aux/vga` support for NVIDIA adapters from early NV4 through several NV4x-era families.

Key behavior:
- Maps NVIDIA MMIO and subdivides it into PFB, PRAMDAC, PEXTDEV, PMC, PTIMER, PFIFO, PRAMIN, PGRAPH, FIFO, and PCRTC register windows.
- `snarf()` finds NVIDIA display-class PCI devices, handles some PCI-X ID quirks, classifies architecture generation, detects crystal frequency, dual-head/two-stage PLL support, laptop LCD devices, framebuffer size, CRTC extension state, PLLs, dither, panel timing, and flat-panel dimensions.
- `clock()` searches PLL `m/n/p` values for single-stage and two-stage PLL families.
- `init()` rejects 24 bpp, handles optional `lcd=` mode attribute, computes hardware cursor placement, PLL values, CRTC overflow bits, blanking, LCD scaling flags, pixel depth, dual-head ownership, and cursor configuration.
- `load()` performs extensive device initialization: unlocks CRTC, initializes PMC/timer, framebuffer regions, PRAMIN object tables, PGRAPH state, PFIFO state, dual-head registers, LCD timing, CRTC extensions, PLL/DAC state, and final CRTC interrupt/display enable.
- `dump()` prints clock calculation, detected architecture/device IDs, CRTC extension state, PLLs, panel state, and dual-head flags.

Important details:
- Large blocks of register programming are architecture- and device-family-specific.
- Framebuffer size detection differs for NV4, nForce/nForce2 integrated devices, and later chips.
- LCD handling is partial and keyed by hard-coded device IDs plus mode attributes.
- The file includes NVIDIA-derived copyright text and is hardware-sensitive; errors in register tables can hang display hardware.

Filesystem relevance:
- Uses `#v/vgactl` type selection and `segattach("nvidiammio")`; it depends on Plan 9’s device namespace for hardware access.
