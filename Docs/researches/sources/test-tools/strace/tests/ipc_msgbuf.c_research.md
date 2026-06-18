<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ipc_msgbuf.c -->
# sources/test-tools/strace/tests/ipc_msgbuf.c

Purpose: Tests message payload decoding for `msgsnd` and `msgrcv`, including message type, text strings, and receive flags.

Important APIs/types/functions: Uses `msgget`, `msgsnd`, `msgrcv`, `msgctl`, direct syscall support through `scno.h`, fixed `text_string`, `cleanup`, and helper routines around a small message buffer.

Control flow: Creates a private message queue, sends a known string payload, receives it with controlled size/type/flags, prints expected decoded buffer contents, and removes the queue during cleanup.

State/persistence behavior: Creates one SysV message queue and one queued message during the test, both scoped to the process and cleaned up explicitly.

Dependencies: Requires SysV message queues, syscall number support, and strace helpers. Xlat wrappers alter flag rendering.

Integration points: Complements `ipc_msg.c` by exercising message payload buffer decoding rather than only control structures.

Risks: Queue creation can fail under tight IPC limits. Payload string length and NUL handling must match the decoder's quoted-string behavior.

Test signals: Output includes `msgget`, `msgsnd`, `msgrcv` with `STRACE_STRING`, cleanup, and final exit.

Source read signal: complete file read for this research pass; file size 101 line(s), 2521 byte(s).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ipc_msgbuf.c -->
