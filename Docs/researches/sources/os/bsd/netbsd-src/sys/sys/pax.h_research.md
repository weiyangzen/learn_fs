# File Research: sources/os/bsd/netbsd-src/sys/sys/pax.h

## Purpose
Defines PaX security feature flags and function hooks for ASLR, MPROTECT, and Segvguard.

## Main API
- Process flags: `P_PAX_ASLR`, `P_PAX_MPROTECT`, `P_PAX_GUARD`.
- Global setup: `pax_init`, `pax_set_flags`, `pax_setup_elf_flags`.
- MPROTECT hooks: `pax_mprotect_maxprotect`, `pax_mprotect_validate`, `pax_mprotect_prot`, plus debug-aware macros.
- Segvguard hooks: `pax_segvguard`, `pax_segvguard_cleanup`.
- ASLR hooks: `PAX_ASLR_DELTA`, `pax_aslr_init_vm`, `pax_aslr_stack`, `pax_aslr_stack_gap`, `pax_aslr_exec_offset`, `pax_aslr_rtld_offset`, `pax_aslr_mmap`.

## Dependencies
Includes `uvm/uvm_extern.h` and forward-declares process, LWP, exec, and vmspace types.

## Risks and Notes
Most functions compile to inline no-ops when their corresponding feature options are disabled. Default ASLR fallback returns deterministic offsets, so callers must not assume randomization unless `PAX_ASLR` is enabled.
