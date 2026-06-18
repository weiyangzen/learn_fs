# File Research: sources/os/bsd/netbsd-src/sys/sys/semaphore.h

Read completely: 44 lines.

This non-public header contains only the POSIX semaphore value limit definition `SEM_VALUE_MAX` as all bits set in an unsigned int. It explicitly tells userland to include `<semaphore.h>` instead.

Risks: no behavior here; the main concern is accidental use as a public API despite the warning.
