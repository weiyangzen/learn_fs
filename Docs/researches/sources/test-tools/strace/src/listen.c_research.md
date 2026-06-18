<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/listen.c -->
# sources/test-tools/strace/src/listen.c

Purpose: decodes the `listen` syscall.
Important APIs/types/functions: `SYS_FUNC(listen)`, `printfd`, and integer backlog printing.
Control flow: prints `sockfd` and `backlog` on entry and returns decoded status. State and persistence behavior: none.
Dependencies and integration points: socket syscall table entry maps to this decoder. Risks: minimal; only fd formatting and signed backlog presentation matter. Test signals: simple listen traces with valid, invalid, and negative backlog values.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/listen.c -->
