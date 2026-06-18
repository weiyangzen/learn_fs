# sources/test-tools/strace/src/syscall.c

Purpose: syscall metadata, personality switching, entry/exit decoding, result formatting, injection/tampering, register access, and architecture glue for the trace loop.

Important APIs/types/functions: `sysent0/1/2`, `ioctlent0/1/2`, `printers0/1/2`, `errnoent`, `signalent`, `nsyscalls`, `current_personality`, `current_wordsize`, `set_personality`, `get_scno`, `syscall_entering_decode`, `syscall_entering_trace`, `syscall_entering_finish`, `syscall_exiting_decode`, `syscall_exiting_trace`, `syscall_exiting_finish`, `tamper_with_syscall_entering`, `tamper_with_syscall_exiting`, `get_instruction_pointer`, `get_stack_pointer`, `set_scno`, `set_error`, and `set_success`.

Control flow: generated syscall tables are included, shorthand macros are removed, and active pointers are switched per personality. On entry, `get_scno` obtains syscall info via `PTRACE_GET_SYSCALL_INFO` or arch registers, shuffles/personality-validates the syscall number, installs a stub for unknown syscalls, reads arguments, decodes indirect subcalls, filters paths/status/fds, optionally injects faults/delays/pokes, captures stack traces, and invokes the syscall printer. On exit, it refreshes result registers, updates mmap/comm/personality state, applies exit-side injection, prints return value/error/aux string/time, performs I/O dumps, and clears per-call flags/private data.

State and persistence behavior: holds active syscall/ioctl/printer vectors, current personality and word sizes, global and per-TCB injection vectors, cached `ptrace_sci`, register-error state, saved temporary error, and per-TCB flags. State is in memory and reset at syscall boundaries or TCB drop.

Dependencies and integration points: central dependency of `strace.c`; includes generated syscall/ioctl/error/signal tables, arch-specific `get_scno.c`, `get_error.c`, register files, ptrace syscall-info helpers, qualifiers, mmap notifications, delay/poke/retval injection, and xlat metadata.

Risks: architecture-specific register layouts, personality detection, syscall-number shuffling, seccomp stop order, unknown syscall stubs, compat argument truncation, and tampering register writes are high-risk. `PTRACE_GET_SYSCALL_INFO` fallback paths must remain coherent with older kernels.

Test signals: normal entry/exit on supported personalities, invalid syscall number, syscall restart errors, raw mode, status filtering, path/fd filtering, I/O dump sets, fault/retval/signal/delay/poke injection, seccomp stops, mmap-changing calls, `PR_SET_NAME`, unknown arch fallbacks, and compat syscall argument truncation.
