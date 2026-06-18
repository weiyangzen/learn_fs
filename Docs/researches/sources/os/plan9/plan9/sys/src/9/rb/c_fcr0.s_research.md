# File Research: sources/os/plan9/plan9/sys/src/9/rb/c_fcr0.s

Tiny MIPS assembly stub for reporting floating-point implementation identity.

Key responsibilities:
- `C_fcr0` returns `0x500`, claiming an R4000-style implementation with LL/SC support.

Role:
- Supports MIPS user/runtime code that probes FCR0 to choose locking/floating-point behavior.

Notable risks:
- It reports a synthetic FP implementation rather than real hardware FP state, matching this port’s FP emulation strategy.
