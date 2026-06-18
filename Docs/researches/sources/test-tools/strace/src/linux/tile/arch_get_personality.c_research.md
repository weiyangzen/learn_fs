# sources/test-tools/strace/src/linux/tile/arch_get_personality.c

## Purpose
Maps `PTRACE_GET_SYSCALL_INFO` audit architecture values to the Tile personality index. It lets strace select the compat Tile table directly from kernel syscall-info metadata.

## Important APIs, Types, and Functions
Implements `get_personality_from_syscall_info(const struct_ptrace_syscall_info *sci)`. It returns true, as integer personality `1`, when `sci->arch` is `AUDIT_ARCH_TILEGX32` or `AUDIT_ARCH_TILEPRO`; otherwise it returns `0` for native TILE-Gx.

## Control Flow and Integration
The function is called through `get_personality.c` when syscall-info data is available. It is a simple boolean expression with no error return. Native Tile stays personality 0; compat Tile uses personality 1.

## State and Persistence
No state is retained. The chosen personality updates the per-tracee `tcb` through the generic personality-selection flow outside this file.

## Dependencies
Depends on `struct_ptrace_syscall_info` and audit arch constants. Its return values must match `arch_defs_.h` personality ordering and the two `syscallent` tables.

## Risks
Assumes any non-compat arch reported to this Tile build is native personality 0. If a future Tile audit arch is introduced, this fallback could classify it as native without an explicit guard.

## Test Signals
Trace native TILE-Gx, TILE-Gx32, and TILEPro syscalls with kernels supporting `PTRACE_GET_SYSCALL_INFO`; verify syscall table selection and printed personality suffixes.
