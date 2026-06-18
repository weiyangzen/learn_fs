# File Research: sources/os/plan9/9front/sys/src/9/xen/xentimer.c

Purpose: 9front Xen timer implementation using Xen shared `vcpu_time_info` and Xen timer VIRQ.

Key behavior:
- `getshadow` reads a consistent copy of per-VCPU time info using Xen version sequencing.
- `xentimerinit` derives CPU frequency from Xen TSC conversion parameters.
- `xentimerset` arms Xen timer with a minimum lead time.
- `xentimerenable` binds `VIRQ_TIMER`.
- `xentimerread` converts TSC cycles to nanoseconds and tracks wallclock base from shared info.
- Provides `xenwallclock`, `microdelay`, `delay`, and `perfticks`.

Integration notes: Uses `HYPERVISOR_shared_info`, `HYPERVISOR_set_timer_op`, `cycles`, `mul64fract`, and Plan 9 timer interrupt code.

Risk/attention points: `getshadow` spins while version is odd; correctness depends on Xen’s seqlock-style update protocol.
