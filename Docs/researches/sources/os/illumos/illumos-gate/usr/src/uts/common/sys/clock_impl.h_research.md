# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/clock_impl.h

`clock_impl.h` contains private lbolt clock implementation definitions for kernel/kmemuser builds. It defines default `HZ`, thresholds for switching between event-driven and cyclic-driven lbolt, and cache-line-conscious per-CPU/global lbolt tracking structures.

It exports lbolt source functions, the hybrid function pointer, soft interrupt hooks, debugger entry/return accounting, and `lb_info`. Macros provide wait-free, fast-path, and no-account lbolt values while compensating for debugger time.
