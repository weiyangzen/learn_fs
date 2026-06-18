# File Research: sources/os/bsd/openbsd-src/sys/sys/kcore.h

This header defines the kernel crash-dump core file format.

Key definitions:
- Magic values: `KCORE_MAGIC`, `KCORESEG_MAGIC`.
- Physical RAM segment descriptor: `phys_ram_seg_t`.
- Crash dump header: `kcore_hdr_t`.
- Segment header: `kcore_seg_t`.

Behavior and integration:
- The format borrows structure from old regular core files in `<sys/core.h>`.
- Uses `u_quad_t` for physical address/size portability across architectures.

Risk notes:
- The header is format ABI for crash dump readers; field widths are chosen for cross-architecture dumps.
