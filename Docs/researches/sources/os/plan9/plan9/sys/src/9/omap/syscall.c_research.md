# File Research: sources/os/plan9/plan9/sys/src/9/omap/syscall.c

ARM syscall, notify/noted, exec register setup, and fork-child register setup for OMAP Plan 9.

Key responsibilities:
- Defines the ARM user notification frame `NFrame`.
- `notify()` arranges delivery of pending Plan 9 notes by copying the current `Ureg` and note text onto the user stack and redirecting PC to `up->notify`.
- `noted()` validates and restores user state after a note handler calls `noted`, supporting `NCONT`, `NRSTR`, `NSAVE`, and default/debug termination paths.
- `syscall()` validates user origin, fetches syscall number/arguments, dispatches through `systab`, handles errors, traces syscall stops, handles `NOTED`, delivers notes, schedules delayed reschedules, and exits through `kexit`.
- `execregs()` sets a new process entry PC and user stack after exec.
- `forkchild()` builds the child `Ureg` frame so `forkret` returns to user mode with `r0 == 0`.

Important behavior:
- Syscall number is in `r0`; arguments are copied from the user stack after a return-PC word.
- `RFORK` triggers FPU state preparation before the syscall.
- `NOTED` calls `noted()` with the stack argument.
- User-altered PSR is masked so system flags cannot be changed across noted return.

Dependencies:
- Depends on `systab`, `sysctab`, Plan 9 process/note/procctl mechanisms, `okaddr`/`validaddr`, and ARM `Ureg` layout.

Notable risks:
- Notify frame ABI is architecture-specific and must match user runtime expectations.
- Syscall argument validation relies on stack range checks and `validaddr` for edge cases.
