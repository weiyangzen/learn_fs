# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/secflags.h

## Role

Defines process security-flag sets, deltas, names, and validation interfaces.

## Key Interfaces

- `secflagset_t` is a 64-bit bitset.
- `psecflags_t` stores effective, inherit, lower, and upper process security flag sets.
- `secflagdelta_t` represents add/remove/assign operations.
- `psecflagwhich_t` selects which process flag set is targeted.
- `secflag_t` currently defines `PROC_SEC_ASLR`, `PROC_SEC_FORBIDNULLMAP`, and `PROC_SEC_NOEXECSTACK`.
- Helper APIs manipulate sets, convert names, validate deltas, produce defaults, and stringify flags.
- Userland exposes `secflags_parse()` and `psecflags()`.
- Kernel exposes `secflag_enabled()`, `secflags_promote()`, and `secflags_apply_delta()`.

## Risk Notes

`PROC_SEC_MASK` defines the valid bit universe. Validation must preserve the lower/effective/inherit/upper constraints or process hardening policy can be bypassed or made impossible to change.
