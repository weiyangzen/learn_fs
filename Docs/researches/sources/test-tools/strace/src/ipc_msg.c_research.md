# sources/test-tools/strace/src/ipc_msg.c

Purpose: decodes SysV message queue creation, send, and receive syscalls.

Important APIs/types/functions: `SYS_FUNC(msgget)`, `SYS_FUNC(msgsnd)`, `SYS_FUNC(msgrcv)`, `tprint_msgsnd`, `tprint_msgrcv`, `fetch_msgrcv_args`, `tprint_msgbuf`, `indirect_ipccall`, and xlats `ipc_msg_flags`, `ipc_private`, `resource_flags`.

Control flow: `msgget` prints key and resource/permission flags. `msgsnd` prints `msqid`, then chooses argument positions based on `indirect_ipccall`. `msgrcv` prints `msqid` on entry and, on exit, decodes direct arguments or the legacy indirect `ipc_kludge` pair before printing `msgflg`.

State and persistence behavior: no durable state. For receive, decoding intentionally happens on exit so returned message content is available; SPARC64/directness uses `get_tcb_priv_ulong` to disambiguate legacy indirect forms.

Dependencies and integration points: relies on `ipc_defs.h` provider selection, message-header layouts, shared message-buffer printer, tracee memory fetch helpers, and SysV IPC syscall table entries.

Risks: indirect IPC argument order is architecture-sensitive. `fetch_msgrcv_args` must respect current tracee word size or signed `msgtyp` may be decoded incorrectly. Tracee memory failures fall back to addresses.

Test signals: cover direct and indirect `msgsnd`/`msgrcv`, IPC_PRIVATE keys, mode-bit combinations, receive success vs error, inaccessible `ipc_kludge`, and 32-bit word-size receive arguments.
