# File Research: sources/os/plan9/9front/sys/src/9/xen/xenbin.c

Purpose: User-space conversion tool that transforms a Plan 9 386 bootable image into a Xen binary-loader-compatible image.

Key behavior:
- Reads Plan 9 executable metadata with `crackhdr`.
- Pads text so the Xen image can load at guest physical address zero.
- Emits a Plan 9 header and 32-byte Xen binary header with magic/checksum/load addresses.
- Page-aligns data and adjusts line-number PC table encoding for debugger consistency.
- Optional `-p` sets the Xen PAE flag.

Integration notes: Uses Plan 9 libc/bio/mach headers and streams input from fd 0 to output fd 1.

Risk/attention points: It assumes valid `crackhdr` results and does little error checking on reads/writes. Arithmetic is 32-bit `long` oriented.
