# File Research: sources/os/bsd/dragonflybsd/sys/sys/kthread.h

Kernel-only process/thread daemon interface. Defines `struct kproc_desc` for starting internal daemons and declares kproc/kthread lifecycle helpers: start, suspend, resume, suspend loop, shutdown, allocation, CPU-specific creation, and exit.

Filesystem relevance: background filesystem, syncer, journal, buffer, VM, and helper threads use this style of kernel thread lifecycle.
