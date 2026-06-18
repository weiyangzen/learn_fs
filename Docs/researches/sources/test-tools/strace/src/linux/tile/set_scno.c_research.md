# sources/test-tools/strace/src/linux/tile/set_scno.c

## Purpose
Changes a Tile tracee's syscall number for syscall injection or tampering.

## Important APIs, Types, and Functions
Defines `arch_set_scno(struct tcb *tcp, kernel_ulong_t scno)`. It refreshes registers with `get_regs(tcp)` when syscall-info data is valid, writes `tile_regs.regs[10] = scno`, and calls `set_regs(tcp->pid)`.

## Control Flow and Integration
Generic `set_scno` invokes this hook. The conditional register refresh prevents overwriting newer register data when `PTRACE_GET_SYSCALL_INFO` supplied syscall metadata without refreshing the architecture register cache.

## State and Persistence
Mutates `tile_regs` and writes the changed register set to the tracee. No durable state exists beyond the tracee's stopped register state.

## Dependencies
Depends on Tile syscall number register `r10`, `ptrace_syscall_info_is_valid`, `get_regs`, and `set_regs`.

## Risks
If register refresh fails, the function returns `-1` and the syscall number is not changed. If the cache is stale and the refresh is skipped, unrelated registers could be written back incorrectly.

## Test Signals
Syscall tampering/injection tests should change Tile syscall numbers and verify the kernel executes or reports the replacement syscall.
