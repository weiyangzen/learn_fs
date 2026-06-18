# sources/test-tools/strace/src/ipc_defs.h

Purpose: central compatibility header for SysV IPC decoders, selecting kernel or libc IPC headers and normalizing structure names.

Important APIs/types/functions: `MSG_H_PROVIDER`, `SEM_H_PROVIDER`, `SHM_H_PROVIDER`, `NAME_OF_STRUCT_MSQID_DS`, `NAME_OF_STRUCT_SEMID_DS`, `NAME_OF_STRUCT_SHMID_DS`, `NAME_OF_STRUCT_SHMINFO`, `NAME_OF_STRUCT_IPC_PERM_KEY`, `IPC_64`, and `PRINTCTL`.

Control flow: preprocessor checks reject `<linux/ipc.h>` when configured structure sizes do not match the active mpers ABI. It then includes either Linux or libc IPC headers, maps provider header names and structure identifiers, defines missing `IPC_64`, and exposes `PRINTCTL` for `IPC_64`-aware command formatting.

State and persistence behavior: no runtime state; all behavior is compile-time configuration and macro expansion.

Dependencies and integration points: used by message, semaphore, and shared-memory decoders. It bridges configure-time size probes, mpers personalities, and generated xlat command tables.

Risks: structure-size probes must stay aligned with kernel/libc headers; choosing the wrong provider would make `umove` decode incompatible layouts. `PRINTCTL` masks only `IPC_64`, so old compat IPC calls remain partly decoded elsewhere.

Test signals: build/test matrix should cover native, m32, mx32, and systems with/without Linux IPC headers; SysV `IPC_SET`, `IPC_STAT`, and info commands should print correct structure field names.
