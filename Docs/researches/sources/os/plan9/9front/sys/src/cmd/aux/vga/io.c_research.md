# File Research: sources/os/plan9/9front/sys/src/cmd/aux/vga/io.c

Provides shared low-level Plan 9 device access for aux/vga. It lazily opens `#P/iob`, `#P/iow`, `#P/iol`, and `#P/msr` for byte/word/long port I/O and MSR reads/writes, plus `#v/vgactl` for VGA control messages.

It parses cached `vgactl` attributes, writes control settings such as type, size, linear aperture, and PCI device, reads BIOS memory from `/dev/realmodemem` or `#P/realmodemem`, and supports BIOS hex dumps.

Utility functions include zeroing allocator `alloc`, palette writes, formatted register/item output, and controller flag printing.
