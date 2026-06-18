# sources/test-tools/strace/src/linux/tile/set_error.c

## Purpose
Implements Tile register mutation for syscall fault injection and return-value tampering.

## Important APIs, Types, and Functions
Defines `arch_set_error(struct tcb *tcp)` and `arch_set_success(struct tcb *tcp)`. The error path writes `tile_regs.regs[0] = -tcp->u_error`; the success path writes `tile_regs.regs[0] = tcp->u_rval`; both call `set_regs(tcp->pid)`.

## Control Flow and Integration
Generic `set_error` calls these hooks when strace injects or changes syscall results. The functions update the cached return register and write the entire register set back to the tracee.

## State and Persistence
Mutates the transient `tile_regs` cache and persists the modification into the stopped tracee through ptrace `set_regs`.

## Dependencies
Depends on `tile_regs`, `set_regs`, and Tile syscall return-value convention.

## Risks
Because only `r0` is set, any consumers expecting `r1` to carry a positive errno may not see a fully canonical Tile return state. Whole-register writes also rely on `tile_regs` being fresh.

## Test Signals
Fault-injection tests should confirm Tile syscalls can be forced to fail with specific errno values and forced to return chosen success values.
