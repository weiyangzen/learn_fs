# sources/test-tools/strace/src/rtc.c

Purpose: Decodes RTC ioctls and nested time/alarm/PLL/parameter structures.

Important APIs/types/functions: `rtc_ioctl`; helpers for `rtc_time`, `rtc_wkalrm`, `rtc_pll_info`, voltage-low flags, and RTC parameter get/set.

Control flow: dispatches by ioctl code. Pure enable/disable commands have no argument; read commands print output on exit; set commands print input on entry. Alarm, PLL, and param commands decode structs, with `RTC_PARAM_GET` showing value changes between entry and exit.

State and persistence: stateless; phase-sensitive output only.

Dependencies/integration: Linux RTC UAPI, ioctl xlat tables, time struct printers, flag/value xlat tables, and generic ioctl dispatcher.

Risks: ioctl structure layouts and param IDs evolve. GET commands must avoid printing output before success; SET commands must not rely on exit memory.

Test signals: RTC time read/set, alarm read/set, IRQ/epoch read, PLL get/set, voltage low read/clear, param get/set, invalid pointers, and no-arg commands.
