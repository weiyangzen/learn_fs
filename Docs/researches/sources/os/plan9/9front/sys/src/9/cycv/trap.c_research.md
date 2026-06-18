# File Research: sources/os/plan9/9front/sys/src/9/cycv/trap.c

Role: Cyclone V ARM trap, syscall, fault, notification, floating-point, process-save, and register setup code.

Key responsibilities:
- Dumps stacks and registers for debugging, including a `ktrace /arm/9cycv` script fragment.
- Decodes ARM fault status values and routes translation/access/domain/permission faults to `fault()`.
- Converts unrecoverable kernel faults into panics and user faults into Plan 9 notes via `faultnote()`.
- Handles undefined-instruction traps, including lazy FPU initialization/restoration for coprocessor 10/11 opcodes.
- Dispatches IRQ traps through `intr()` and syscalls through `dosyscall()`.
- Builds and validates user notification frames in `notify()`/`noted()`.
- Saves/restores FPU state around notes and process switches.
- Sets initial kernel/user register state for fork, exec, and kernel process children.

Dependencies:
- Uses ARM Ureg layout, fault status registers (`getifsr`, `getdfsr`, etc.), FPU helpers, Plan 9 note/syscall/fault machinery, and scheduler entry points.

Notes and risks:
- `faulterr[0x01]` string says "alignement fault" as in source.
- `notefpsave()` returns nil, so note-time FPU save exposure is not implemented here.
- `procsave()` always switches back to the kernel L1 table after saving active FPU state.
