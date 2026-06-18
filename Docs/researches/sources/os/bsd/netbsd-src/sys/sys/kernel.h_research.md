# File Research: sources/os/bsd/netbsd-src/sys/sys/kernel.h

Declares core kernel globals for `_KERNEL` or standalone builds: host/domain names, RTC offset, boot/shutdown state, clock tick variables, statistics/profiling frequencies, profiling source, and `getticks()`.

This is a low-level coordination header used broadly by kernel subsystems. It has no structures or algorithms, but its globals are timing and boot-state contracts. Risks involve initialization order and consumers assuming valid values before `cold` clears.
