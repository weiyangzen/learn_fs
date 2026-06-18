# File Research: sources/os/bsd/netbsd-src/sys/kern/subr_copy.c

## Summary
Provides generic `uio` transfer helpers, arbitrary-process/vmspace copy helpers, ioctl kernel/user copy selection, and generic user-space fetch/store/CAS wrappers.

## Main Responsibilities
- Implements `uiomove()`, `uiopeek()`, `uioskip()`, `ureadc()`, and `uiomove_frombuf()`.
- Copies data to/from arbitrary `vmspace` or `proc` objects through direct copy or `uvm_io()`.
- Supports `FKIOCTL` paths via `ioctl_copyin()`/`ioctl_copyout()`.
- Implements generic `_ucas_32()` and `_ucas_64()` when the port does not provide full user CAS.
- Exposes checked `ucas_*`, `ufetch_*`, and `ustore_*` entry points plus legacy aliases.

## Important Behavior
`uiomove()` mutates the caller's `uio` and iovecs while `uiopeek()` performs the same transfer without advancing the original `uio`. Both use `copyin_vmspace()`/`copyout_vmspace()` and call `preempt_point()` for user vmspaces.

Generic user CAS wires the target user page before entering the critical section. On MP platforms without native MP user CAS, it uses a CPU-wide IPI gate, `cpu_lock`, and `splhigh()` to keep other CPUs from racing the fetch/store pair.

## Dependencies
Uses UVM vmspace references, process lookup, `uvm_io()`, `uvm_vslock()`, IPI/cpu locking for generic MP CAS, and machine-provided low-level `_ufetch_*`/`_ustore_*` primitives.

## Risks
The arbitrary-vmspace copy path depends on correct `uio_rw` direction conventions for `uvm_io()`. The generic CAS fallback is intentionally heavyweight and correctness depends on page wiring and the IPI gate memory-ordering protocol.
