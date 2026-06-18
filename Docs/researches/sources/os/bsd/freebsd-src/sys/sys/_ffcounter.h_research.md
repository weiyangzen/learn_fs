# File Research: sources/os/bsd/freebsd-src/sys/sys/_ffcounter.h

Feed-forward clock counter typedef.

Key elements:
- Defines `ffcounter` as `uint64_t`.
- Describes it as a wide monotonic counter accumulating at the selected timecounter rate.

Dependencies:
- Assumes `uint64_t` is visible from including context.

Research notes:
- Minimal ABI/type shim for feed-forward clock consumers.
- Relevant to timestamping paths that may affect I/O accounting or filesystem timing.
