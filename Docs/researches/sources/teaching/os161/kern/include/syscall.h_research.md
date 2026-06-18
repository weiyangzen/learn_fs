# File Research: sources/teaching/os161/kern/include/syscall.h

Declares the system call entry and process entry helpers. `syscall(struct trapframe *tf)` is the dispatcher called from trap handling. `enter_forked_process(struct trapframe *tf)` is a student-supplied helper for fork return in the child. `enter_new_process(argc, argv, env, stackptr, entrypoint)` transitions to user mode and is marked `__DEAD`.

The file also declares in-kernel syscall implementations for reboot and time: `sys_reboot` and `sys___time`.

It bridges machine trapframes, user pointer types, virtual addresses, and syscall implementations. Correctness depends on trapframe ownership, user/kernel pointer validation, and not returning from user-mode entry.
