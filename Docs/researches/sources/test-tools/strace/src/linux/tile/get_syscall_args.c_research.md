# sources/test-tools/strace/src/linux/tile/get_syscall_args.c

## Purpose
Copies Tile syscall arguments from registers into strace's normalized argument array.

## Important APIs, Types, and Functions
Defines `arch_get_syscall_args(struct tcb *tcp)`. It maps `tile_regs.regs[0]` through `regs[5]` to `tcp->u_arg[0]` through `u_arg[5]` and returns `1`.

## Control Flow and Integration
Generic `get_syscall_args` calls this after syscall number resolution. There is no conditional logic; Tile uses six argument registers starting at `r0`.

## State and Persistence
Mutates only `tcp->u_arg[]` for the current syscall. Reads the transient register cache.

## Dependencies
Depends on Tile register layout, `struct tcb`, and generic syscall argument decoding.

## Risks
If Tile ABI argument order changes or register cache is stale, every syscall decoder receives wrong arguments. No local error path validates register availability.

## Test Signals
Trace syscalls with six distinct arguments, such as `mmap`, `clone`, or `pselect6`, and verify each printed argument matches the tracee call.
