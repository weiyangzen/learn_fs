# sources/test-tools/fio/os/windows/posix/include/sys/ipc.h

Purpose: placeholder System V IPC header for Windows.

Important APIs/types: none in this file; related IPC constants and typedefs are in `sys/shm.h`.

Control flow and state: no logic or state.

Dependencies and integration: satisfies includes for code paths that also include `sys/shm.h`.

Risks: not a complete IPC header; callers expecting `IPC_CREAT`, `key_t`, or permission structures from this header alone will fail.

Test signals: Windows build and include-order checks for shared-memory users.
