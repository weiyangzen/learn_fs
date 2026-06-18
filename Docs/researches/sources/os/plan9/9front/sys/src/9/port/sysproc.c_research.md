# File Research: sources/os/plan9/9front/sys/src/9/port/sysproc.c

Plan 9 process, exec, notification, segment, rendezvous, semaphore, time, and syscall dispatch implementation.

Key responsibilities:
- Implements `rfork` for both in-place group changes and new process creation.
- Duplicates or shares process segments, file groups, namespace groups, rendezvous groups, and environment groups according to rfork flags.
- Implements `exec`, including `#!` interpreter chaining, a.out header parsing, stack/TOS/argv construction, image cache attachment, segment replacement, close-on-exec, and register setup.
- Implements sleep/yield, alarms, exits, wait/await, errstr exchange, and notify/noted delivery.
- Implements segment syscalls: `segbrk`, `segattach`, `segdetach`, `segfree`, and old `brk`.
- Implements Plan 9 rendezvous by matching sleeping processes by tag in the rendezvous group hash.
- Implements user semaphores with segment-local wait lists, compare-and-swap, blocking/timed acquire, release, and careful wakeup race handling.
- Implements nanosecond time syscall compatibility.
- Implements central syscall dispatch in `dosyscall()`, including argument validation, syscall tracing stop points, error-to-return conversion, and `NOTED` special handling.

Dependencies:
- Interacts heavily with segment/image code, file groups, process groups, scheduler, note/trap architecture hooks, EDF scheduling, and syscall tables.
- Includes generated syscall table definitions through `systab.h`.

Notable behavior:
- `sysexec()` uses a temporary `ESEG` stack until commit, then relocates it to `SSEG`.
- Interpreter recursion is limited to 8 levels.
- User semaphore commentary documents subtle sleep/wakeup races and notes verification with a Spin model.
- `dosyscall()` swaps `errstr`/`syserrstr` on failure so user `errstr` sees the correct error.
