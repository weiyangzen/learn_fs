# File Research: sources/os/bsd/dragonflybsd/sys/sys/rtprio.h

This header defines the realtime-priority ABI used by `rtprio()` and DragonFly's LWP-specific realtime-priority call.

Key responsibilities:
- Defines priority classes:
  - `RTP_PRIO_REALTIME`
  - `RTP_PRIO_NORMAL`
  - `RTP_PRIO_IDLE`
  - `RTP_PRIO_THREAD`
  - `RTP_PRIO_FIFO`
- Provides helper macros:
  - `RTP_PRIO_BASE()`
  - `RTP_PRIO_IS_REALTIME()`
  - `RTP_PRIO_NEED_RR()`
- Defines priority range:
  - `RTP_PRIO_MIN` is highest priority
  - `RTP_PRIO_MAX` is lowest priority
- Defines syscall operations:
  - `RTP_LOOKUP`
  - `RTP_SET`
- Defines `struct rtprio` with `type` and `prio`.
- Declares userland `rtprio()` and `lwp_rtprio()`.

Important invariants:
- `RTP_PRIO_FIFO` is represented as realtime with `RTP_PRIO_FIFO_BIT` set.
- `RTP_PRIO_NEED_RR()` treats FIFO as the non-round-robin exception.
- LWP realtime-priority declaration is guarded by `_LWP_RTPRIO_DECLARED`.

Research notes:
- This is a small ABI header for scheduling policy control, not the scheduler implementation.
