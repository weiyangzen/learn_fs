<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/membarrier.c -->
# sources/test-tools/strace/src/membarrier.c

Purpose: decodes `membarrier` command, flags, and optional CPU argument.
Important APIs/types/functions: `SYS_FUNC(membarrier)`, `membarrier_cmds`, `membarrier_flags`, and `MEMBARRIER_CMD_FLAG_CPU`.
Control flow: on entry prints command and flags; if the command requires CPU flag, also prints `cpu_id`, otherwise prints the third argument as raw `flags`/reserved value. State and persistence behavior: none.
Dependencies and integration points: syscall table and xlat definitions. Risks: command-specific optional arguments must track kernel API growth. Test signals: query, register, private expedited, CPU-targeted, and unknown flag traces.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/membarrier.c -->
