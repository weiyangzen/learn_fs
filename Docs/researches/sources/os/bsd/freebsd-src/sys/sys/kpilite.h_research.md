# File Research: sources/os/bsd/freebsd-src/sys/sys/kpilite.h

Defines lightweight scheduler pin/unpin helpers for restricted kernel builds where offsets are available and modules are tied. It includes generated `offset.inc`.

`sched_pin_lite()` and `sched_unpin_lite()` operate on `struct thread_lite`, assert the target is `curthread`, maintain `td_pinned`, and use interrupt fences around pin-state changes. It is a narrow KPI subset for code that cannot use full thread definitions.
