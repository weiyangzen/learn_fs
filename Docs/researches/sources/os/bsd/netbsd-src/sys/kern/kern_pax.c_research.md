# File Research: sources/os/bsd/netbsd-src/sys/kern/kern_pax.c

## Purpose
Implements NetBSD PaX exploit-mitigation policy: ASLR, MPROTECT W^X enforcement, and SEGVGUARD crash throttling, controlled by compile-time options, ELF PaX notes, process flags, and sysctls.

## Main Interfaces
- `pax_init`: adjusts maximum stack mapping for ASLR stack waste.
- `pax_setup_elf_flags`, `pax_set_flags`: derive process PaX flags from ELF notes and apply ptrace exception policy.
- MPROTECT: `pax_mprotect_maxprotect`, `pax_mprotect_validate`, `pax_mprotect_prot`.
- ASLR: `pax_aslr_init_vm`, `pax_aslr_mmap`, `pax_aslr_exec_offset`, `pax_aslr_rtld_offset`, `pax_aslr_stack`, `pax_aslr_stack_gap`.
- SEGVGUARD: `pax_segvguard`, `pax_segvguard_cleanup`.
- Sysctl setup under `security.pax`.

## Internal State And Dependencies
- Feature blocks are guarded by `PAX_ASLR`, `PAX_MPROTECT`, and `PAX_SEGVGUARD`.
- Sysctl tunables control enabled/global modes, ptrace override, debug flags, ASLR lengths, segvguard expiry/suspension/max crashes.
- Uses CSPRNG `cprng_fast32`, ELF note flags, proc `p_pax`, UVM protections and vmspace ASLR deltas, vnode `v_segvguard`, credentials, `exec_lock`, and syslog.

## Control Flow Notes
- ELF flags opt in/out depending on global policy: global mode applies unless a NO flag is present; non-global mode applies only when the feature flag is present.
- MPROTECT rejects simultaneous write+execute mappings for protected processes and can allow ptrace extraction override.
- ASLR computes mmap, exec, rtld, stack, and stack-gap offsets with alignment and 32-bit/topdown distinctions.
- SEGVGUARD stores crash history per executable vnode and uid. Repeated crashes within expiry suspend execution for a configured interval; later exec attempts return `EPERM` while suspended.

## Locking And Correctness
- `pax_segvguard` requires `exec_lock`; crash updates require write-held `exec_lock`.
- `pax_segvguard_cleanup` frees all per-vnode uid entries.
- ASLR debug mode can force deterministic random values or disable subfeatures.

## Risk Areas
- ASLR entropy and placement depend on architecture-provided constants such as `PAX_ASLR_DELTA_EXEC_LEN`.
- MPROTECT ptrace policy intentionally weakens W^X for debugging when enabled.
- SEGVGUARD state is attached to vnodes and must be cleaned during vnode lifecycle.
- Process flag setup must happen during exec before VM layout decisions.

## Filesystem Relevance
Moderate. SEGVGUARD stores per-executable state on vnodes, and PaX behavior is derived from executable ELF metadata loaded through exec/VFS paths.
