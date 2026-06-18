# File Research: sources/os/bsd/netbsd-src/sys/kern/subr_pcu.c

## Purpose
Implements the MI Per CPU Unit framework, used to manage LWP-owned per-CPU hardware context such as FPU state. It coordinates lazy load, save, discard, and release of machine-dependent PCU units across CPU migration and remote ownership.

## Main Entry Points
- `pcu_switchpoint()` releases state when the current LWP switches away from the CPU holding its PCU state.
- `pcu_load()` loads or initializes the current LWP's PCU state on the current CPU.
- `pcu_discard_all()`, `pcu_save_all()`, `pcu_discard()`, `pcu_save()`, and `pcu_save_all_on_cpu()` manage state during exec, exit, coredump, explicit discard/save, and CPU-local flushing.
- `pcu_valid_p()` reports whether an LWP's state for a unit is considered valid.

## Control Flow And State
The file is compiled only when `PCU_UNIT_COUNT > 0`. Per-unit state is tracked in `lwp_t::l_pcu_valid`, `lwp_t::l_pcu_cpu[id]`, and `cpu_info::ci_pcu_curlwp[id]`. Machine-dependent operations come from `pcu_ops_md_defs[id]`.

All state transitions happen at `splpcu()`/high IPL. If a target state is local, `pcu_do_op()` calls MD save/release callbacks directly. If the state resides on a remote CPU, `pcu_lwp_op()` sends an IPI to run `pcu_cpu_ipi()`, waits for completion, and handles races where ownership changed first. `pcu_load()` saves/releases any remote state for the current LWP, evicts any other LWP currently loaded on this CPU, then calls the MD load callback with `PCU_VALID` or fresh-state flags and records ownership.

## Dependencies
Depends on MD `pcu_ops_t` callbacks, CPU/LWP fields, IPL/IPI infrastructure, and scheduler context-switch hooks.

## Risks And Notes
The framework's invariants are strict: only the current CPU may mutate `ci_pcu_curlwp[id]`, and only the CPU holding loaded state may clear `l_pcu_cpu[id]`. Incorrect MD callbacks or missing high-IPL protection can corrupt lazy hardware context. Several assertions encode special cases for system LWPs, suspended LWPs, and failed LWP creation paths.
