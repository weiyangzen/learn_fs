# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/clock_highres.c

This file registers the `CLOCK_HIGHRES` backend. It exposes monotonic high-resolution time from `gethrtime()` and implements high-resolution POSIX timers using the cyclic subsystem.

Core behavior:
- `clock_highres_gettime()` converts `gethrtime()` to `timespec_t`; `clock_highres_getres()` reports `cyclic_getres()`.
- `clock_highres_settime()` always returns `EINVAL`; this clock is not settable.
- Timer creation allocates a `cyclic_id_t` slot in `it->it_arg` and stores the generic timer fire callback.
- `clock_highres_timer_settime()` clamps sub-`clock_highres_interval_min` one-shot or interval values to 200 us for callers without `proc_clock_highres`.
- Existing one-shot timers can be reprogrammed directly with `cyclic_reprogram()` instead of being removed and re-added.
- Nonzero timers are installed as low-level cyclic handlers and then bound to the current thread’s CPU and processor-set binding.
- One-shot timers are represented with `CY_INFINITY` interval so they remain until `timer_settime()` or delete removes them.
- `clock_highres_fire()` atomically records the last fire time in `it_hrtime` before calling `it_fire()`.
- `clock_highres_timer_gettime()` computes remaining time from the original start, interval, current hrtime, and last recorded fire.
- `clock_highres_timer_lwpbind()` rebinds an active cyclic after LWP binding changes.
- `clock_highres_init()` fills the backend vector and registers it with `clock_add_backend(CLOCK_HIGHRES, ...)`.

Important invariants:
- Cyclic add/remove/rebind operations are performed under `cpu_lock`.
- Process binding state is sampled under `p_lock` while `cpu_lock` keeps CPU/partition objects stable.
- Overflow is checked for initial start plus interval; later wrap is accepted as practically unreachable.
- `it_itime.it_value` is converted to an absolute fire time for reporting, even when caller passed a relative timeout.
