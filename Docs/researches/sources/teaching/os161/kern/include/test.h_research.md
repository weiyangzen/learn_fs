# File Research: sources/teaching/os161/kern/include/test.h

Central declaration header for OS/161 kernel tests, boot/menu entry points, and synchronization problem drivers. It declares tests for arrays, bitmaps, thread lists, threads, semaphores, locks, CVs, RW locks, filesystem stress, kmalloc, networking, HMAC, and automation deadlock/livelock checks.

It also declares `runprogram`, `menu`, and `kmain`. Optional blocks are controlled by generated config headers `opt-synchprobs.h` and `opt-automationtest.h`. Synchronization-problem hooks cover whalemating and stoplight primitives.

The `kprintf_t`/`kprintf_n` macros switch output behavior under `SECRET_TESTING`, with `silent` discarding formatted output. This file is mostly test surface area, but it influences automated grading and kernel diagnostics.
