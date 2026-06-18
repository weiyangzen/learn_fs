# sources/test-tools/strace/src/ipc.c

Purpose: generic decoder for the multiplexed legacy `ipc` syscall.

Important APIs/types/functions: `SYS_FUNC(ipc)`, `ipc_arg_name`, `n_args`, `printxval_u`, `ipccalls`, and flag/shift printing helpers.

Control flow: argument 0 is split into a high 16-bit version and low 16-bit IPC call number. The decoder prints the version as a shifted flag component when nonzero, prints the call xlat, then prints all remaining syscall arguments as hex under generic names `first`, `second`, `third`, `ptr`, and `fifth`.

State and persistence behavior: no persistent state and no tracee memory reads; this decoder does not dispatch to specific SysV IPC decoders.

Dependencies and integration points: depends on `defs.h` and generated `xlat/ipccalls.h`; complements the dedicated `msg*`, `sem*`, and `shm*` decoders used for direct syscalls or architecture-specific paths.

Risks: because this is a generic multiplexor printer, it does not decode pointed-to IPC structures. The argument-name array assumes the maximum argument count after `call` fits five entries.

Test signals: multiplexed IPC tests should verify versioned call rendering, xlat fallback for unknown calls, and hex formatting of each remaining argument.
