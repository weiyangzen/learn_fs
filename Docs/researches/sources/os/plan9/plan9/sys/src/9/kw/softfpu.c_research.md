# File Research: sources/os/plan9/plan9/sys/src/9/kw/softfpu.c

## Role

Soft-FPU integration shim for the Kirkwood port. It provides the Plan 9 kernel FPU hook functions while delegating actual FP instruction emulation to `fpiarm`.

This is CPU emulation glue, not filesystem code.

## Main Interfaces

- `fpudevprocio`
- `fpunotify`
- `fpunoted`
- `fpusysrfork`
- `fpusysrforkchild`
- `fpuprocsave`
- `fpuprocrestore`
- `fpusysprocsetup`
- `fpuinit`
- `fpuemu`

## Important Behavior

- Most process lifecycle hooks are no-ops because FP state is stored in the `Proc`.
- `fpudevprocio` rejects access with `"no floating point status"`.
- `fpuemu` calls `fpiarm(ureg)`.

## Dependencies And Assumptions

- Assumes software FP emulation only; no hardware FPU context management is needed.
- Depends on `fpiarm.c`.

## Notable Risks

- Exposes no useful FPU status through device/proc IO.
- Hardware FPU support would require replacing these no-op hooks.
