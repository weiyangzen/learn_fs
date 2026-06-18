# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/x86_64/sys/getcontext.S

## Summary
Implements x86_64 `_getcontext()` with weak `getcontext` alias.

## Key Details
- Calls `SYS_getcontext`.
- Stores the caller return address as saved RIP.
- Stores caller stack pointer after the return address as saved user RSP.
- Stores zero into the saved RAX register.
- Returns zero.

## Notes
The source hard-codes offsets for `uc_mcontext`, `_REG_RAX`, `_REG_RIP`, and `_REG_URSP`.
