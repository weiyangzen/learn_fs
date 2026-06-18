# File Research: sources/os/bsd/openbsd-src/sys/kern/kern_exec.c

## Purpose
Implements `execve(2)` image replacement: executable validation, argument/environment copying, VM command execution, stack setup, credentials/security transitions, fd cleanup, and shared signal/timekeep page mapping.

## Main Responsibilities
- Frees image-loader package allocations with `exec_free_package()`.
- Validates executable vnodes in `check_exec()`.
- Implements `sys_execve()` end to end.
- Copies argv/env strings and auxiliary pointer space with `copyargs()`.
- Creates and maps the shared signal trampoline object in `exec_sigcode_map()`.
- Creates and maps the shared read-only timekeep page in `exec_timekeep_map()`.

## Key Exec Flow
1. Enters single-threading and marks `PS_INEXEC`.
2. Performs namei lookup with pledge/unveil exec constraints.
3. Uses `check_exec()` to verify regular executable file, mount flags, execute permission, and loader compatibility.
4. Copies fake interpreter args, argv, and env into a kernel arg buffer.
5. Calculates stack gap randomization and final stack footprint.
6. Commits by killing other threads, clearing profiling, and replacing the vmspace.
7. Runs loader VM commands and maps stack/guard regions.
8. Copies argv/env and `ps_strings` to user stack.
9. Resets fd flags, signals, TCB, kbind state, pledge/unveil state, timers, and accounting details.
10. Handles setuid/setgid credential transitions and ensures fd 0/1/2 are open for sugid exec.
11. Maps timekeep and signal trampoline pages, calls ELF fixup and machine register setup, then returns `EJUSTRETURN`.

## Security and Policy
- Honors `MNT_NOEXEC` and `MNT_NOSUID`.
- Blocks sugid programs under exec promises.
- Clears unveil state unless exec pledge is active.
- Clears tracing for unprivileged traced setuid/setgid exec.
- Sets `PS_SUGID`, `PS_SUGIDEXEC`, and image flags such as `PSI_WXNEEDED`, `PSI_PROFILE`, `PSI_NOBTCFI`.

## Failure Modes
Before commit, errors unwind package, vnode, namei, and arg-buffer state. After VM replacement, fatal failures call `exit1(..., SIGABRT, EXIT_NORMAL)`.

## Dependencies
Uses VFS/namei, exec switch loaders, UVM, signal subsystem, file descriptors, pledge/unveil, credentials, ktrace, timers, and machine-specific register/mapping hooks.

## Research Notes
This file is the process image transition boundary; it coordinates most per-process security and address-space state.
