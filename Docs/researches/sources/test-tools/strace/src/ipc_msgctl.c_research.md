# sources/test-tools/strace/src/ipc_msgctl.c

Purpose: mpers-aware decoder for `msgctl` message queue control operations.

Important APIs/types/functions: `SYS_FUNC(msgctl)`, `print_ipc_perm`, `print_msqid_ds`, `print_msginfo`, `msqid_ds_t`, `DEF_MPERS_TYPE`, `MPERS_DEFS`, `PRINTCTL`, and `msgctl_flags`.

Control flow: the decoder locates `buf` according to direct or indirect IPC calling convention and strips `IPC_64` for command dispatch. On entry it prints `msqid` and `op`; `IPC_SET` decodes `msqid_ds` immediately, status/info commands defer to exit, and unknown commands print the raw buffer address. On exit it decodes queue status structures or `msginfo`.

State and persistence behavior: no persisted private state; the buffer address is recomputed from syscall arguments on both phases. Tracee memory is read only for structure output.

Dependencies and integration points: depends on `ipc_defs.h` layout selection, mpers-generated structure definitions, field-printing helpers, and SysV message queue xlat tables.

Risks: old compat IPC calls are explicitly not fully decoded. `IPC_SET` prints a reduced permission subset while status commands include key/creator fields; tests must not expect identical field sets.

Test signals: exercise `IPC_SET`, `IPC_STAT`, `MSG_STAT`, `MSG_STAT_ANY`, `IPC_INFO`, `MSG_INFO`, unknown commands, inaccessible buffers, and native/compat layouts.
