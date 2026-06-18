# sources/test-tools/strace/src/ipc_semctl.c

Purpose: mpers-aware decoder for `semctl` control operations and semaphore information structures.

Important APIs/types/functions: `SYS_FUNC(semctl)`, `print_ipc_perm`, `print_semid_ds`, `print_seminfo`, `semun_ptr_t`, `semid_ds_t`, `DEF_MPERS_TYPE`, `PRINTCTL`, `set_tcb_priv_ulong`, and `get_tcb_priv_ulong`.

Control flow: on entry the decoder prints `semid`, `semnum`, command, and resolves `arg`, including the indirect `union semun` pointer form for legacy IPC and SPARC64 personality handling. `IPC_SET` decodes immediately; stat/info commands save the resolved address and decode on exit; unknown commands print the address with indirect markers when needed.

State and persistence behavior: per-syscall private `tcb` storage preserves the resolved buffer address across entry/exit. No durable global state.

Dependencies and integration points: uses mpers type generation, IPC provider macros, semaphore xlat flags, and tracee memory fetch helpers. Integrated with the SysV semaphore syscall decoder table.

Risks: old compat IPC calls are not fully decoded. Indirect pointer handling is subtle and architecture dependent; failing to save the resolved address would break exit-only decoding.

Test signals: cover `IPC_SET`, `IPC_STAT`, `SEM_STAT`, `SEM_STAT_ANY`, `IPC_INFO`, `SEM_INFO`, indirect semun pointers, inaccessible pointers, and native/compat structure sizes.
