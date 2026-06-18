# File Research: sources/os/bsd/netbsd-src/sys/kern/sys_process.c

## Purpose
Provides process memory access support used by ptrace and ktrace, plus a hook symbol required by ptrace module linkage.

## Main Interfaces
- `process_domem`: performs traced-process memory I/O through `uvm_io`.
- `ptrace_hooks`: dummy symbol under `PTRACE_HOOKS` so `ptrace_common` load fails if hooks are unavailable.

## State And Control Flow
`process_domem` rejects zero-length operations early, checks the target LWP is not exiting and its VM space is live, takes a VM-space reference, performs `uvm_io` with PaX mprotect-derived access, optionally calls `pmap_procwr` after successful writes on machines needing instruction-cache/process-write maintenance, then releases the VM-space reference.

## Dependencies And Integration
Depends on target process VM space, UVM map I/O, PaX mprotect policy, machine pmap hooks, ptrace/ktrace configuration, and LWP exit state.

## Risks And Edge Cases
- Target VM lifetime is protected by explicit `uvmspace_addref`/`uvmspace_free`.
- Writes may need machine-dependent coherency repair via `pmap_procwr`.
- Access permissions are mediated through `pax_mprotect_prot`.

## Filesystem Relevance
Low. It is process debugging memory I/O support, not filesystem logic, though ptrace can observe or modify processes performing filesystem operations.
