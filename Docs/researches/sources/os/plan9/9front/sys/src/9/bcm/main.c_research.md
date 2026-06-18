# File Research: sources/os/plan9/9front/sys/src/9/bcm/main.c

32-bit BCM kernel startup, memory sizing, initial user process setup, and reboot support.

Key responsibilities:
- Initializes `Mach` state for CPU0 and secondary CPUs.
- Parses boot arguments and `plan9.ini` data.
- Brings up memory, pools, printing, UART console, screen, traps, VFP, timers, pages, processes, devices, and scheduler.
- Builds initial `/boot/boot` argv and enters user mode in `init0()`.
- Computes kernel/user memory split and kernel pool sizes in `confinit()`.
- Implements reboot trampoline setup using embedded `rebootcode`.
- Provides platform stubs such as `isaconfig()` and `setupwatchpts()`.

Important behavior:
- Enforces minimum Raspberry Pi firmware revision/date.
- Uses mailbox/VideoCore information for RAM and device data.
- `exit()` reboots after stopping interrupts and devices.

Dependencies:
- Port kernel initialization APIs, BCM mailbox helpers, MMU/reboot assembly, scheduler, console, screen, and Plan 9 process bootstrap.
