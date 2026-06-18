<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/print_msgbuf.c -->
# sources/test-tools/strace/src/print_msgbuf.c

Purpose: mpers-aware printer for SysV message buffers.

Important APIs/types/functions: `tprint_msgbuf`, `msgbuf_t`, and `MSG_H_PROVIDER`.

Control flow: fetches the message header, prints signed `mtype`, then prints `mtext` from immediately after `mtype` using the caller-provided byte count.

State and persistence behavior: no state.

Dependencies and integration points: used by SysV `msgsnd`/`msgrcv` decoders; depends on IPC header provider selection and mpers message-buffer layout.

Risks: text length is supplied by the caller and must match syscall semantics. Compat `mtype` layout matters.

Test signals: send/receive message buffers, zero-length text, invalid pointer, native/compat mtype widths, and truncated string output.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/print_msgbuf.c -->
