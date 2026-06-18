<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/personality.c -->
# sources/test-tools/strace/src/personality.c

Purpose: decodes the Linux `personality` syscall argument.

Important APIs/types/functions: `SYS_FUNC(personality)`, `personality_types`, and `personality_flags`.

Control flow: prints the low personality type bits with `PER_*` xlat and remaining behavior flags with `ADDR_*`/personality flag xlat semantics.

State and persistence behavior: no persistent state in the decoder; the syscall changes tracee execution personality in the kernel.

Dependencies and integration points: integrated through syscall table and generated personality xlat tables.

Risks: flag/type masks must match kernel UAPI. Unknown flags should remain visible numerically.

Test signals: known personalities, combined flags, unknown high bits, and `0xffffffff` query-style argument.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/personality.c -->
