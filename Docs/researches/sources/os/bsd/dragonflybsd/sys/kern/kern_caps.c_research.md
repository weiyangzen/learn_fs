# File Research: sources/os/bsd/dragonflybsd/sys/kern/kern_caps.c

## Summary
Implements DragonFly syscall capability restriction helpers and `syscap_get`/`syscap_set` syscalls. Capabilities here are restriction bits stored in credentials and checked alongside root/group/jail policy.

## Main Responsibilities
- Provides `sys_syscap_get` and `sys_syscap_set`.
- Implements exec-time capability inheritance in `caps_exec`.
- Provides raw and checked helpers: `caps_get`, `caps_set_locked`, `caps_priv_check`, `caps_priv_check_td`, and `caps_priv_check_self`.
- Checks parent-process capability state when `__SYSCAP_INPARENT` is requested.

## Important Behavior
`syscap_set` only adds restriction bits; it compares requested flags with current state and atomically creates a new credential with `cratom_proc` when changes are needed. It also marks `SYSCAP_ANY` bits.

`caps_exec` shifts EXEC restriction bits into SELF bits and preserves EXEC bits across exec. `caps_priv_check` enforces root unless `__SYSCAP_NOROOTTEST` is present, optionally permits wheel via `__SYSCAP_WHEELOK`, then checks credential capability bits and jail restrictions.

## Risks
The `kern.caps_available` sysctl is declared but not consulted in this implementation. Resource data for syscaps is effectively unimplemented here; `syscap_get` returns an EOF marker and `syscap_set` rejects non-null data.
