# File Research: sources/os/bsd/netbsd-src/sys/kern/sys_ptrace.c

## Purpose
Provides the native `ptrace(2)` syscall wrapper, native ABI copy methods, register method table, and module registration for ptrace.

## Main Interfaces
- `sys_ptrace`: forwards native ptrace requests to `do_ptrace`.
- `native_ptm`: native `struct ptrace_methods` containing copyin/copyout helpers and register callbacks.
- `ptrace_copyin_piod`, `ptrace_copyout_piod`: validate/copy `ptrace_io_desc`.
- `ptrace_copyin_siginfo`, `ptrace_copyout_siginfo`, `ptrace_copyout_lwpstatus`.
- `ptrace_init`, `ptrace_fini`, `ptrace_modcmd`: establish/disestablish `SYS_ptrace` for `emul_netbsd`.

## State And Control Flow
The native syscall extracts request, pid, address, and data arguments, then delegates all policy and operation logic to `sys_ptrace_common.c`. The module declares dependency on `ptrace_common`.

## Dependencies And Integration
Depends on `ptrace_common`, syscall package establishment, native process register helpers from `sys_process_lwpstatus.c`, and the NetBSD emulation switch.

## Risks And Edge Cases
- Copy helpers enforce exact ABI sizes for siginfo and optional exact-or-zero size for `ptrace_io_desc`.
- If syscall establishment/disestablishment fails, module init/fini reports the error directly.
- Most safety policy lives in `do_ptrace`, not this wrapper.

## Filesystem Relevance
Low. Native ptrace syscall plumbing is process-debugging infrastructure, not filesystem code.
