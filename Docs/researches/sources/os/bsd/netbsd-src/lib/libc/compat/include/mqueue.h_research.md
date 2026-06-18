# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/include/mqueue.h

Declares compatibility POSIX message queue timed operations.

It exposes old `mq_timedreceive` and `mq_timedsend` using `timespec50`, plus modern `__mq_timedreceive50` and `__mq_timedsend50` using `timespec`.

This is time32/time64 compatibility for message queues.
