# File Research: sources/os/plan9/plan9/sys/src/cmd/upas/bayes/dump.c

- Role: Diagnostic utility for compiling and dumping one regexp as DFA.
- Behavior: Compiles `argv[1]`, converts it with `dregcvt`, prints state/case ranges, then tests remaining arguments with `dregexec`.
- Integration: Includes libregexp internals and `dfa.h`.
- Risks/notes: Minimal argument validation; assumes at least one regexp argument.
