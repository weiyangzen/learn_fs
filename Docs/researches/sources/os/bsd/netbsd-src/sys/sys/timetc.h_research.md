# File Research: sources/os/bsd/netbsd-src/sys/sys/timetc.h

Read completely: 95 lines.

Defines the kernel timecounter hardware interface.

Key elements:
- Kernel or kmem-user only.
- `MAX_TCNAMELEN` sets recommended sysctl-controllable counter name length.
- `struct timecounter` contains callbacks to read the counter and poll PPS, counter mask, frequency, name, quality, private pointer, and next pointer.
- Kernel declarations include active `timecounter`, `tc_getfrequency`, `tc_init`, `tc_detach`, `tc_setclock`, `tc_ticktock`, and `tc_gonebad`.
- Optionally declares `_kern_timecounter` sysctl node.

Risks and notes:
- Timecounter quality and frequency determine system timekeeping correctness.
- Counter rollover and mask correctness are hardware-driver responsibilities.
