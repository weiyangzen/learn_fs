# File Research: sources/os/plan9/plan9/sys/src/9/bcm/archbcm.c

BCM2835/Raspberry Pi architecture glue for reset, reboot, watchdog feeding, CPU identification, and Ethernet controller discovery.

Key behavior:
- `archreset()` enables floating point via `fpon()`.
- `archreboot()` programs BCM power/watchdog registers under `POWERREGS` to trigger reset, then spins forever.
- `wdogfeed()` refreshes the watchdog with a 5-second timeout; `wdogoff()` disables watchdog reset configuration.
- `archbcmlink()` registers watchdog feeding on the clock callback list at `HZ`.
- `cpuidprint()` reports a single ARM1176JZF-S CPU and measured MHz.
- `archether()` exposes controller 0 as a USB Ethernet device with 100 Mbps nominal speed.

Dependencies include `io.h` interrupt/register constants, `arm.h`, Plan 9 netif/Ether structures, and global `m`.
