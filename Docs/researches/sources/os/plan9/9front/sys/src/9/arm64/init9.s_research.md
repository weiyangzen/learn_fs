# File Research: sources/os/plan9/9front/sys/src/9/arm64/init9.s

Tiny Plan 9 user init entry stub.

Key behavior:
- Loads static base into `R28`.
- Passes the kernel `boot` function address in `R0`.
- Branches to `startboot`.

Dependencies:
- Relies on Plan 9 ARM64 ABI conventions and boot support elsewhere.

Research notes:
- This file is only the assembly bridge into the userland boot startup path.
