# File Research: sources/os/bsd/netbsd-src/sys/sys/lwpctl.h

Defines the user-visible per-LWP control block layout and kernel allocation structures. `lwpctl_t` exposes current CPU and performance counter fields with fixed 32/64-bit-compatible size constraints. Feature bits advertise supported fields. Kernel-only `lcpage` and `lcproc` manage mapped pages of control blocks with bitmaps and UVM objects.

Risks are ABI layout stability, page bitmap sizing, and correct cleanup on LWP exit. This supports fast userland access to LWP CPU/counter information.
