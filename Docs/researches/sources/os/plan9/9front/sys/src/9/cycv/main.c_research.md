# File Research: sources/os/plan9/9front/sys/src/9/cycv/main.c

Cyclone V kernel startup, configuration parsing, and initial user process setup.

Key responsibilities:
- Implements reboot/exit stubs and address-alignment checks.
- Sets up process MMU state during fork/setup.
- Parses boot configuration options from the boot config area.
- Initializes memory configuration and kernel/user split.
- Creates initial process environment and enters user mode.
- Runs kernel initialization sequence: UART, memory, MMU, interrupts, timers, pools, pages, processes, devices, and scheduler.
- Provides `getconf()`, `isaconfig()`, CPUID print, sanity checks, and watchpoint stub.

Important behavior:
- Uses fixed config buffer sizing.
- Service mode and memory split are driven by parsed config variables.
- Starts from a relatively small platform-specific sequence compared with BCM.

Dependencies:
- Cyclone V MMU/trap/timer/interrupt code, Plan 9 port initialization, UART console, and user bootstrap.
