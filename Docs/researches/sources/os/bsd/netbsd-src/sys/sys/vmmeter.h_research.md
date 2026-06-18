# File Research: sources/os/bsd/netbsd-src/sys/sys/vmmeter.h

Read completely: 56 lines.

Defines the legacy `struct vmtotal` snapshot of systemwide VM/process totals computed periodically, historically used by VM statistics interfaces.

Fields covered:
- Runnable, disk-wait, page-wait, and sleeping-in-core process counts.
- Total and active virtual memory.
- Total and active real memory.
- Shared virtual/real memory totals and active shared counts.
- Free memory pages.

Risks and notes:
- This is an ABI-style statistics structure with fixed-width signed fields; consumers should treat values as periodic snapshots, not live counters.
