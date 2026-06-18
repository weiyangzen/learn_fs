# File Research: sources/os/bsd/openbsd-src/sys/sys/timetc.h

Defines the kernel/libc timecounter interface and rejects ordinary userland inclusion. `struct timecounter` describes hardware counters through a read callback, mask, frequency, quality, name, private pointer, user exposure flag, list linkage, frequency adjustment, and computed precision.

`struct timekeep` is the shared timekeeping data layout with generation, scale, offsets, boottime, naptime, and counter mask/user flags. Exports include `tc_init`, quality reset, setclock, realtime clock set, tick processing, sysctl, frequency/time adjustment, and global `timecounter`, `timekeep_object`, and `timekeep`.
