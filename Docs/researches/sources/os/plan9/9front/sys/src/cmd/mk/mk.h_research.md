# File Research: sources/os/plan9/9front/sys/src/cmd/mk/mk.h

Defines mk’s core data structures, flags, globals, debug masks, and utility macros.

Key behavior:
- Defines `Bufblock`, `Word`, `Symtab`, `Rule`, `Arc`, `Node`, and `Job`.
- Enumerates symbol-table spaces for variables, targets, times, nodes, aggregates, export controls, overrides, cached out-of-date checks, and internal state.
- Defines rule attributes (`META`, `UPD`, `QUIET`, `VIR`, `REGEXP`, `NOREC`, `DEL`, etc.) and node state flags.
- Defines parsing helpers, debug masks, and `PERCENT()` meta marker logic.

Important dependencies: Plan 9 `<u.h>`, `<libc.h>`, `<bio.h>`, `<regexp.h>`, and `fns.h`.

Notable risks:
- Flag bits are shared across modules; mismatches affect graph, scheduling, and cleanup behavior.
