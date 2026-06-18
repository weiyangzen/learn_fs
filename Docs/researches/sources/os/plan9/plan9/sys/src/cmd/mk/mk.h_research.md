# File Research: sources/os/plan9/plan9/sys/src/cmd/mk/mk.h

Central definitions for Plan 9 `mk`.

Defines:
- `Bufblock`, `Word`, `Envy`, `Rule`, `Arc`, `Node`, `Job`, `Symtab`.
- Rule attribute bits: `META`, `UPD`, `QUIET`, `VIR`, `REGEXP`, `NOREC`, `DEL`, `NOVIRT`, etc.
- Node flag bits: `VIRTUAL`, `CYCLE`, `READY`, `CANPRETEND`, `PRETENDING`, `NOTMADE`, `BEINGMADE`, `MADE`, `PROBABLE`, `VACUOUS`, etc.
- Symbol-table spaces for variables, targets, file times, nodes, archive aggregates, exported variables, and internal variables.
- Debug flags and parser helpers.

Role:
- Brings in Plan 9 headers, regexp support, global variable declarations, macros, and `fns.h`.
