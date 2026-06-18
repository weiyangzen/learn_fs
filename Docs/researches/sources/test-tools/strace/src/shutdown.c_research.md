# sources/test-tools/strace/src/shutdown.c

Purpose: decodes the socket `shutdown` syscall.

Important APIs/types/functions: `SYS_FUNC(shutdown)`, `printfd`, and `shutdown_modes` xlat table.

Control flow: prints socket fd and `how` as `SHUT_RD`, `SHUT_WR`, `SHUT_RDWR`, or unknown.

State and persistence behavior: stateless; no tracee memory reads.

Dependencies and integration points: included in socket syscall decoding and depends on `<sys/socket.h>` constants.

Risks: minimal; only xlat coverage for platform constants matters.

Test signals: known shutdown modes, unknown numeric mode, and fd path annotations.
