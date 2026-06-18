# File Research: sources/os/bsd/freebsd-src/sys/kern/sys_process.c

## Purpose
Implements process debugging support centered on `ptrace(2)`, including register access, traced-process memory I/O, VM map inspection, thread/LWP debug metadata, coredump requests, remote syscall execution, and ptrace relationship management.

## Main Elements
- Register helpers: `proc_read_regs()`, `proc_write_regs()`, `proc_read_fpregs()`, `proc_write_fpregs()`, `proc_read_dbregs()`, `proc_write_dbregs()` call machine-dependent register accessors with privilege checks for writes.
- Regset helpers: `proc_find_regset()`, `proc_read_regset()`, `proc_write_regset()` expose ELF-note-style dynamic register sets through `struct iovec`.
- 32-bit compatibility wrappers expose 32-bit register layouts and prevent unsafe 32-bit debugger writes to 64-bit targets.
- `proc_sstep()`: enables single-step execution through machine ptrace support.
- `proc_rwmem()`, `proc_readmem()`, `proc_writemem()`: read/write another process address space one page at a time via VM faults, held pages, `uiomove_fromphys()`, and instruction-cache sync for executable writes.
- `ptrace_vm_entry()`: enumerates VM map entries, protections, offsets, timestamps, vnode path, fsid, and fileid for `PT_VM_ENTRY`.
- `sys_ptrace()`: marshals user arguments into kernel buffers for every ptrace request, performs copyin/copyout, and delegates request execution to `kern_ptrace()`.
- `proc_set_traced()`, `ptrace_unsuspend()`, `proc_can_ptrace()`: manage tracing state, stopped-process eligibility, parent/debugger checks, and resumption.
- `kern_ptrace()`: central request dispatcher for attach/detach, continue/step/syscall tracing, event masks, syscall args/returns, memory I/O, registers, LWP info/lists, VM timestamps/entries, coredump requests, remote syscalls, and machine-dependent ptrace extensions.

## Dependencies And Integration
Connects process, thread, signal, VM, vnode, file descriptor, audit, syscall, and machine-dependent register subsystems. It relies on `proctree_lock`, `PROC_LOCK`, process holds, ptrace flags, `p_candebug()`, `p_cansee()`, VM map/object locking, and Capsicum rights for coredump fd access.

## Risk Notes
This is a high-risk security boundary. It enforces visibility/debug permissions, rejects system processes, serializes parallel ptrace requests with `P2_PTRACEREQ`, and uses privilege checks for memory/register writes. Lock ordering and lock drops around allocation, copyin/copyout, VM faults, and remote requests are central to avoiding deadlocks and races with exiting or reparented processes.
