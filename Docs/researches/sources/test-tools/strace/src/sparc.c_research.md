# sources/test-tools/strace/src/sparc.c

Purpose: SPARC-specific decoder for `kern_features` return flags.

Important APIs/types/functions: `SYS_FUNC(kern_features)` and `sparc_kern_features` xlat table.

Control flow: compiled only for SPARC/SPARC64. It does nothing on entry or syscall error; on successful exit it formats the return value as flag names in `tcp->auxstr` and asks return-value formatting to show both hex and string.

State and persistence behavior: no persistent state beyond assigning transient auxstr.

Dependencies and integration points: architecture syscall table and return formatting.

Risks: xlat table must track kernel feature bits; no argument decoding exists because the syscall exposes feature flags via return value.

Test signals: successful return with single/multiple bits, unknown bits, and error path without aux string.
