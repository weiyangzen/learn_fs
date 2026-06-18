# sources/test-tools/strace/src/linux/tile/get_error.c

## Purpose
Decodes Tile syscall return values and errno into `tcp->u_rval` and `tcp->u_error`.

## Important APIs, Types, and Functions
Includes `negated_errno.h` and defines `arch_get_error(struct tcb *tcp, const bool check_errno)`. It reads `tile_regs.regs[0]`, calls `is_negated_errno`, writes `tcp->u_rval = -1` and positive `u_error` for negative errno, otherwise stores the raw return in `u_rval`.

## Control Flow and Integration
Generic `get_error` calls this function after syscall exit. Although the Tile calling convention has `r0` as value or negative errno and `r1` as zero or positive errno, the code intentionally relies on `r0` because older kernels did not expose the updated `r1` in ptregs at this point.

## State and Persistence
Mutates only the current tracee control block fields `u_rval` and `u_error`. It reads the transient `tile_regs` cache.

## Dependencies
Depends on `tile_regs` from `arch_regs.c`, `is_negated_errno`, `struct tcb`, and the generic syscall-exit path.

## Risks
The historical `r1` workaround is correct for old kernels but means decoding is entirely dependent on negative-errno encoding in `r0`. If Tile kernel behavior diverges, errno reporting could be wrong.

## Test Signals
Trace Tile syscalls that succeed, return large positive values, and fail with common errors such as `ENOENT`. Fault-injection tests should verify printed errno uses `u_error` and success values preserve `u_rval`.
