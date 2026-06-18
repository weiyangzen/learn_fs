# sources/test-tools/strace/src/linux/32/subcallent.h

## Purpose

`sources/test-tools/strace/src/linux/32/subcallent.h` adapts the generic Linux indirect socket/IPC subcall table for 32-bit time32 personalities. It temporarily maps the generic `sys_recvmmsg` and `sys_semtimedop` decoder names to the 32-bit time variants before including `../generic/subcallent.h`, then undefines the mappings.

This keeps the generic subcall numbering and metadata while ensuring legacy indirect `socketcall`/`ipc` subcalls that pass timeout structures use `recvmmsg_time32` and `semtimedop_time32` decoders on 32-bit ABIs.

## Important APIs, Types, And Data Shape

The file defines two preprocessor aliases:

```c
#define sys_semtimedop sys_semtimedop_time32
#define sys_recvmmsg sys_recvmmsg_time32
```

The included generic table emits `struct_sysent` initializer rows using `SEN(recvmmsg)` and `SEN(semtimedop)`. Because `SEN` ultimately references `sys_...` decoder symbols, these aliases redirect only the two timeout-bearing indirect subcalls. After inclusion, both aliases are undefined to avoid affecting later syscall table fragments.

The generic dependency requires `SYS_socket_subcall` to be defined by the including architecture table and uses `TRACE_INDIRECT_SUBCALL` plus normal syscall flags such as `TN`, `TI`, `TM`, and `SI`.

## Control Flow

There is no runtime control flow in this wrapper. The compile-time flow is: define aliases, include the generic subcall table, then undefine aliases. The generic table emits entries for socket subcalls 1 through 20 and IPC subcalls, with `SYS_ipc_subcall` derived from `SYS_socket_subcall + SYS_socket_nsubcalls`.

At runtime, the resulting table rows are used by strace syscall dispatch when a traced 32-bit architecture exposes indirect socket or IPC multiplexing. `src/syscall.c` contains subcall handling paths guarded by `SYS_socket_subcall`.

## State And Persistence Behavior

This file has no mutable state or persistence. Its only lasting effect is compiled read-only syscall table data where the two affected indirect subcalls point at time32 decoders instead of the generic names.

## Dependencies

Dependencies are `../generic/subcallent.h`, architecture syscall tables that define `SYS_socket_subcall`, decoder symbols for `sys_recvmmsg_time32` and `sys_semtimedop_time32`, syscall table macros such as `SEN`, and trace classification flags from the surrounding strace syscall table infrastructure.

## Integration Points

Several 32-bit architecture tables include this wrapper after defining `SYS_socket_subcall`, including i386, arm, m68k, s390, sparc, powerpc, sh, and mips o32/n32 variants. It integrates with time32 decoder implementations in `mmsghdr.c` and `ipc_sem.c`, and with the generic indirect-subcall dispatch logic in `src/syscall.c`.

## Risks

The primary risk is leaking the temporary macro aliases beyond the include; the explicit `#undef` lines prevent that. If an architecture includes this file without defining `SYS_socket_subcall`, the generic table deliberately raises a preprocessor error. If a 32-bit ABI actually needs time64 indirect decoding for these legacy subcalls, this wrapper would route it incorrectly; the contract is that this is the 32-bit time32 subcall wrapper. Changes to names in `generic/subcallent.h` or `SEN` expansion can also break the aliasing trick.

## Test Signals

Useful signals are successful builds for 32-bit architectures that include this file, `tests/nsyscalls.c` coverage of `SYS_socket_subcall + 1`, syscall decoding tests for indirect `recvmmsg` and `semtimedop` with 32-bit timeout structures, and compile checks showing no `sys_recvmmsg`/`sys_semtimedop` macro leakage into following table includes.
