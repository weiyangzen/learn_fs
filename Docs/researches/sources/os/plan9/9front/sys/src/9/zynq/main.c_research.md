# File Research: sources/os/plan9/9front/sys/src/9/zynq/main.c

Purpose: Zynq kernel initialization and platform lifecycle code.

Key behavior:
- `exit` shuts down CPUs, clears private pages on CPU0, and idles forever.
- L2 cache setup and physical-cache maintenance helpers.
- `options` parses boot configuration at `CONFADDR`.
- `confinit` defines memory/process/page-pool sizing for a 1 GiB system.
- `init0` initializes devices/environment and enters user `boot`.
- `mpinit` optionally starts CPU1 via OCM bootstrap pointer and synchronizes counters.
- `main` performs platform boot sequence: UART/MMU/L2/intr/options/conf/timer/print/proc/segments/links/arch/devices/page/screen/user/scheduler.
- Stubs `reboot`, `isaconfig`, `setupwatchpts`.

Integration notes: Coordinates almost every Zynq subsystem and portable Plan 9 kernel initialization.

Risk/attention points: Memory sizing is hardcoded around 1 GiB. Multiprocessor startup can be disabled with `*nomp`; otherwise CPU1 setup relies on OCM bootstrap conventions.
