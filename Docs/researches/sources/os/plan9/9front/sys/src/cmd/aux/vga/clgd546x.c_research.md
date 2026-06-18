# File Research: sources/os/plan9/9front/sys/src/cmd/aux/vga/clgd546x.c

Implements Cirrus Logic Laguna CL-GD546x PCI controller support. It finds supported Cirrus PCI device IDs, attaches MMIO, records frame-buffer aperture sizing, saves VGA extended registers, and snapshots Laguna-specific MMIO registers such as format, threshold, tiling, vendor-specific control, and 2D control.

`init` supports only 8-bit modes despite containing partial format branches for deeper modes. It reuses `clgd54xxclock`, computes CRT overflow bits, optionally enables linear mode, and configures tile/fetch/interleave control from resolution and memory-bank count.

`load` writes sequencer/CRT/graphics registers and the Laguna MMIO registers. `clgd546xhwgc` is an empty hardware-cursor registration.
