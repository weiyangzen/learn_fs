# File Research: sources/os/bsd/netbsd-src/sys/kern/sys_ptrace_common.c

## Purpose
Implements common ptrace policy and operations shared by native/compat frontends: attach/detach, memory I/O, register access dispatch, event masks, signal info/pass masks, LWP enumeration/status, stop/resume, syscall tracing, coredump requests, and module-level kauth listener setup.

## Main Interfaces
- `do_ptrace`: central request dispatcher.
- Policy helpers: `ptrace_listener_cb`, `ptrace_find`, `ptrace_allowed`, `ptrace_needs_hold`.
- Signal/event helpers: `ptrace_get_siginfo`, `ptrace_set_siginfo`, `ptrace_get_sigpass`, `ptrace_set_sigpass`, `ptrace_get_event_mask`, `ptrace_set_event_mask`, `ptrace_get_process_state`.
- LWP helpers: `ptrace_lwpinfo`, `ptrace_lwpstatus`, `ptrace_startstop`.
- I/O helpers: `ptrace_doio`, `ptrace_regs`, `ptrace_dumpcore`, `process_auxv_offset`.
- Module hooks: `ptrace_common_init`, `ptrace_common_fini`, `ptrace_common_modcmd`.

## State And Control Flow
`do_ptrace` enters `proc_lock`, finds the target, validates ptrace permission and kauth policy, obtains a target LWP reference, optionally releases process locks for requests that do not require them, and dispatches by request. Attach reparents and stops the target. Detach clears traced flags, signal-pass state, syscall tracing, parentage, and single-step state. Continue/step/syscall requests validate signal numbers, optional LWP targeting, deadlock hazards, program counter updates, and single-step state before resuming or signaling.

## Dependencies And Integration
Integrates with process hierarchy/reparenting, process locks/ref locks, LWP references, kauth process authorization, PaX/VM memory I/O through `process_domem`, register helpers via `ptrace_methods`, RAS protection, signal delivery, syscall tracing internals, coredump module hooks, compat hooks, and machine-dependent ptrace requests.

## Risks And Edge Cases
- Lock handling is intentionally request-dependent; incorrect `pheld`/reference logic would risk races with exit/exec or lock leaks.
- Chroot containment is enforced for attach and memory/register access via `proc_isunder`.
- Deadlock checks prevent resuming only suspended/debug-suspended LWPs.
- `PT_READ_*`/`PT_WRITE_*` preserve legacy success semantics even for incomplete or zero transfers.
- `PT_SYSCALLEMU` requires syscall tracing state and stopped target.
- `process_auxv_offset` reconstructs AUXV location from ps_strings and handles 32-bit targets.

## Filesystem Relevance
Low direct relevance. It is debugger/process-control infrastructure, although it can read/write traced process memory and inspect processes performing filesystem calls.
