# File Research: sources/os/plan9/9front/sys/src/9/kw/lexception.s

Kirkwood ARM exception-vector assembly. It defines the vector stubs copied by `trapinit`, the vector table, syscall/SWI entry, undefined instruction, prefetch abort, data abort, IRQ, FIQ, mode switching to SVC, and trap-frame save/restore paths.

`_vsvc` handles syscalls from SVC mode and calls `syscall`. `_vswitch` transitions from exception modes into SVC mode and distinguishes user vs kernel-origin traps based on SPSR. Both paths build a Plan 9 `Ureg`, reload kernel static base and extern-register state, call `trap`, then restore registers and return with `RFE`.

The file also provides `setr13` for installing per-mode stacks.

Notable risks: several comments address Plan 9 assembler `MOVM` ambiguity; correctness depends on exact `Ureg` layout and banked ARM register behavior.
