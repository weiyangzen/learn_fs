# File Research: sources/os/plan9/plan9/sys/src/cmd/db/defs.h

Common definitions and global declarations for the Plan 9 `db` debugger.

Key contents:
- Includes Plan 9 C, libc, bio, ctype, and mach headers.
- Defines core types:
  - `WORD` as `ulong`
  - `ADDR` as `uvlong`
  - `BOOL` as `int`.
- Defines limits and constants: `MAXOFF`, `INCDIR`, `DBNAME`, `CMD_VERBS`, line/argument/symbol sizes, truth values.
- Defines run modes and breakpoint states.
- Defines `BKPT` structure for breakpoints.
- Declares global debugger state:
  - expression/address/count values
  - dot/dotinc
  - symbol/core file paths and fds
  - process state
  - maps
  - breakpoint list
  - input chars.
- Includes `BADREG` and note handling limits.

Research notes:
- This header is intentionally broad and shared across all `db` modules.
- `CMD_VERBS` is used by input parsing to distinguish file references from command syntax.
