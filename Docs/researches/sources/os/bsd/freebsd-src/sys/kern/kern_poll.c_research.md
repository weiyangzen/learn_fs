# File Research: sources/os/bsd/freebsd-src/sys/kern/kern_poll.c

Read completely: 582 lines.

## Purpose
Implements legacy device polling for network interfaces, allowing drivers to replace interrupt-driven packet processing with clock/netisr/idle-loop polling and adaptive burst sizing.

## Main Elements
- Defines sysctls under `kern.polling` for burst size, max burst, per-handler burst, idle polling, user CPU fraction, register-check interval, and diagnostic counters.
- `init_device_poll()` initializes the polling mutex and shutdown handler.
- `hardclock_device_poll()` runs from hardclock, schedules `NETISR_POLL`, tracks pending/lost polls, short ticks, suspect phases, and stalls.
- `ether_poll()` runs polling handlers from the idle loop under NET_EPOCH.
- `netisr_poll()` invokes registered handlers with `POLL_ONLY` or periodic `POLL_AND_CHECK_STATUS`, consuming a chunk of the residual burst.
- `netisr_pollmore()` runs after other netisrs, adapts `poll_burst` based on measured kernel network processing time, and reschedules if work remains.
- `ether_poll_register()` adds an interface/handler pair, rejects duplicates and table overflow, and wakes idle polling.
- `ether_poll_deregister()` removes an interface by replacing it with the last table entry.
- `poll_idle()` is a low-priority kernel process that polls in the idle loop when enabled.
- SYSINIT creates the polling infrastructure and starts the `idlepoll` kproc.

## Dependencies And Integration
Uses network interfaces, netisr polling hooks, NET_EPOCH, hardclock, kernel threads, scheduler priorities, eventhandlers, sysctl, and `IFCAP_POLLING` driver integration.

## Risk Notes
The handler table is fixed at 128 entries. Polling holds `poll_mtx` while calling handlers, so handlers must be short and must follow polling assumptions. Adaptive burst sizing tries to avoid livelock and excessive user CPU starvation but can still record stalls when handlers run too long.
