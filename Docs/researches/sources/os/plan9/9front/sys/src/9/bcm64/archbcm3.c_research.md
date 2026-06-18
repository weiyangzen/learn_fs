# File Research: sources/os/plan9/9front/sys/src/9/bcm64/archbcm3.c

BCM2837/Raspberry Pi 3 architecture support for the ARM64 kernel.

Key responsibilities:
- Implements reset/reboot watchdog control.
- Feeds/disables the watchdog.
- Reports CPU type/name and prints CPUID information.
- Determines CPU count.
- Clears and writes per-CPU mailbox wake registers.
- Wakes secondary CPUs through mailbox plus event signaling.
- Registers the BCM3 architecture link hook.

Dependencies:
- Power/watchdog registers, ARM64 CPU ID helpers, mailbox layout, `sev()`, and architecture dispatch/link registration.
