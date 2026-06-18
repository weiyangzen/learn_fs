# File Research: sources/os/bsd/openbsd-src/sys/kern/sys_process.c

Implements `ptrace(2)` and process memory access helpers when `PTRACE` is enabled, plus common process I/O permission checks used outside the conditional block.

Main entry points:
- `sys_ptrace()`: dispatches ptrace requests, centralizes user/kernel copyin/copyout handling, and allocates temporary register/xstate buffers where needed.
- `ptrace_ctrl()`: handles trace control operations such as trace-me, attach, detach, continue, kill, and optional single-step.
- `ptrace_kstate()`: handles kernel state queries and updates such as thread iteration, event masks, and process-state snapshots.
- `ptrace_ustate()`: handles target memory access, register access, auxiliary vector reads, stack cookie/PAC mask queries, and optional machine xstate operations.
- `process_domem()`: maps ptrace memory I/O to `uvm_io()` against the target process VM map.

Request handling:
- `sys_ptrace()` classifies each request as no-copy, fixed stack copy, allocated input, allocated output, or input-output.
- Kernel-state requests use fixed local structs for thread state, events, and process state.
- Register and extended register requests allocate buffers sized to the machine structures.
- `PT_IO` updates the requested length by subtracting remaining `uio_resid`.

Permission and state checks:
- `process_checktracestate()` requires the target to be traced by the caller, not in exec, and, for thread-specific operations, stopped and waited.
- `PT_ATTACH` rejects self-attach, system processes, already traced processes, exec-in-progress targets, unauthorized uid/sugid targets, disallowed non-child tracing unless privileged or `global_ptrace`, protected init, and ancestor cycles.
- `process_checkioperm()` separately protects target memory access from unauthorized users, setuid/setgid exec targets, init at securelevel, and exec-in-progress processes.

Process/thread lookup:
- `process_tprfind()` accepts either a process id or thread id offset by `THREAD_PID_OFFSET`, returning the process and a selected target thread.
- Process-state APIs expose traced thread ids as offset thread ids.

Filesystem/storage relevance:
- No filesystem implementation. Relevant because debuggers and proc-like tooling depend on safe cross-process VM access, `uio` setup, and kernel permission rules that interact with file-backed mappings and executable image state.
