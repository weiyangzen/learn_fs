# sources/test-tools/strace/src/trace_event.h

Purpose: declares the internal event enum passed from wait classification to trace dispatch.

Important APIs/types/functions: `enum trace_event` values `TE_BREAK`, `TE_NEXT`, `TE_RESTART`, `TE_SYSCALL_STOP`, `TE_SIGNAL_DELIVERY_STOP`, `TE_SIGNALLED`, `TE_GROUP_STOP`, `TE_EXITED`, `TE_STOP_BEFORE_EXECVE`, `TE_STOP_BEFORE_EXIT`, and `TE_SECCOMP`.

Control flow: `strace.c:next_event` creates these values and `dispatch_event` interprets them as break, continue, restart, syscall decode, signal print/delivery, exit/drop, exec handling, or seccomp handling.

State and persistence behavior: type-only header; no state.

Dependencies and integration points: shared by the main trace loop and wait-data structures.

Risks: enum ordering is not externally serialized, but adding values requires updating all dispatch switches.

Test signals: wait-status classification for every enum value and compiler warnings for unhandled enum cases where enabled.
