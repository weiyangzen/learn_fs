# File Research: sources/os/plan9/9front/sys/src/cmd/db/defs.h

Purpose: Shared definitions for the `db` debugger.

Contents:
- Includes Plan 9 base headers, bio, ctype, and `mach.h`.
- Defines debugger scalar types: `WORD` as `ulong`, `ADDR` as `uvlong`, and `BOOL`.
- Defines command constants, input sizes, run modes, breakpoint states, standard fds, and default include directory.
- Defines `BKPT`, holding address, saved instruction bytes, counts, flag, command text, and list link.
- Declares common globals for expression values, dot, files, process state, maps, breakpoints, and input state.

Notable details:
- `CMD_VERBS` is used to identify debugger command delimiters and file-location parsing.
- The header is intentionally broad; implementation prototypes live in `fns.h`.
