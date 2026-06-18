# File Research: sources/os/bsd/netbsd-src/sys/sys/pcu.h

## Purpose
Declares Processor Control Unit state-management hooks for lazy per-LWP machine-dependent CPU resources such as FPU/vector state.

## Main API
- `PCU_UNIT_COUNT`, defaulting to zero.
- When units exist: `pcu_ops_t` with state save/load/release callbacks.
- Flags: `PCU_VALID`, `PCU_REENABLE`.
- Functions: `pcu_switchpoint`, `pcu_discard_all`, `pcu_save_all`, `pcu_load`, `pcu_save`, `pcu_save_all_on_cpu`, `pcu_discard`, `pcu_valid_p`.
- MD operation table: `pcu_ops_md_defs`.

## Dependencies
Requires kernel or kmem-user context; uses `lwp_t` and boolean support.

## Risks and Notes
If `PCU_UNIT_COUNT` is zero, high-level calls become empty macros. Machine-dependent code must correctly detect and trap future PCU use after `pcu_state_release`.
