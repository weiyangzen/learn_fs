# sources/test-tools/stress-ng/stress-vm-segv.c

## Purpose
Implements the `vm-segv` stressor. It forks children, deliberately unmaps portions of their address space, and verifies that valid children die with `SIGSEGV`.

## Important APIs, types, and functions
`stress_vm_segv()` is the stressor entry point. `vm_unmap_child()` attempts broad unmaps while flushing cache/icache, `vm_unmap_self()` unmaps code pages around itself, and `vm_unmap_stack()` unmaps pages around a stack variable after optional `mprotect()`. It uses `fork()`, `pipe()`, `read()`, `write()`, `munmap()`, `mprotect()`, `sigprocmask()`, `shim_waitpid()`, and stress-ng process/OOM/kill helpers.

## Control flow
The parent synchronizes, creates a pipe, forks, waits for `MSG_CHILD_STARTED`, then waits for a child `SIGSEGV` and increments bogo count when seen. The child writes the start token, blocks `SIGSEGV`, applies stress-ng child settings, then tries child-wide, self-code, and stack unmapping before exiting failure if it somehow survives.

## State and persistence
State is per iteration: pipe fds, child PID, wait status, and `test_valid`. No persistent state is written. The bogo counter records observed `SIGSEGV` deaths.

## Dependencies and integration points
Registered as `stress_vm_segv_info` with `CLASS_VM | CLASS_MEMORY | CLASS_OS` and `VERIFY_ALWAYS`. It depends on stress-ng cache flush, OOM adjustment, scheduler, dumpability, fork retry, and kill/wait helpers. Platform guards avoid self-unmap on Apple and some cache flushes on BSDs.

## Risks and edge cases
The file intentionally corrupts child VM state. Pipe/fork failures are resource failures, wrong or missing start tokens cause cleanup without validation, and platforms may differ in self-unmap or stack-unmap behavior. A run with a valid child but no `SIGSEGV` is a test failure.

## Test signals
Expected signal is at least one valid child terminated by `SIGSEGV`. Failure is `no SIGSEGV signals detected`; resource paths report pipe/fork problems.
