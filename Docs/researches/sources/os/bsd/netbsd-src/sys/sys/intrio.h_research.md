# File Research: sources/os/bsd/netbsd-src/sys/sys/intrio.h

Defines ioctl data structures for interrupt affinity and interrupt listing. `intrio_set` carries an interrupt ID plus user CPU set buffer metadata. `intrio_list` describes a variable-sized result buffer containing `intrio_list_line` entries, each with interrupt ID, device name, and per-CPU assignment/count data.

It depends on `sys/intr.h` for identifier sizes and `sys/sched.h` for `cpuset_t`. ABI care is required around `INTRIO_LIST_VERSION`, `il_linesize`, `il_lineoffset`, and the one-element flexible CPU array used for `ncpu`-sized records.
