# sources/test-tools/stress-ng/core-resources.h

Purpose: defines the cross-platform resource bundle used by `core-resources.c` and declares the allocate/access/free API.

Important APIs/types/functions: `stress_resources_t` has sentinel-backed fields for heap/mmap/sbrk memory, pipes, files, sockets, optional eventfd/memfd/userfaultfd/tmpfile, pthreads and locks, inotify, PTYs, timers, POSIX/SysV semaphores, message queues, pkeys, and pidfds. `stress_resources_allocate`, `stress_resources_access`, and `stress_resources_free` form the lifecycle.

Control flow: no runtime logic, but extensive `#if` gates ensure the struct layout only includes resources supported by the build.

State and persistence: the struct is caller-owned. Many fields represent live kernel resources that must be passed back to `stress_resources_free` for cleanup.

Dependencies/integration: includes socket, IPC, queue, semaphore, C11 thread, pthread, killpid, mmap, and syscall feature headers. It also defines `HAVE_USERFAULTFD` from `__NR_userfaultfd`.

Risks: ABI/layout differs by platform feature macros, so code must not serialize this struct or assume stable offsets. Callers must initialize via allocation helper or manually match sentinels before freeing.

Test signals: compile across feature combinations and assert that allocation/free can be called with zero resources, partial allocation, and interrupted runs.
