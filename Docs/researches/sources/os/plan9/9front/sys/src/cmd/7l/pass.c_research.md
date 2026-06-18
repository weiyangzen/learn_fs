# File Research: sources/os/plan9/9front/sys/src/cmd/7l/pass.c

General linker passes for parsing constants, laying out data, following/reordering control flow, and patching branches.

Key functions:
- `atolwhex` parses signed decimal, octal, and hex integers.
- `rnd` rounds values up to an alignment.
- `dodata` validates data initializers, assigns data/BSS addresses, aligns objects, defines linker symbols like `bdata`, `edata`, `end`, and `etext`.
- `brchain` follows chains of unconditional branches.
- `follow` creates a new instruction order using `xfol`.
- `xfol` lays out reachable code, inverts simple branches when useful, copies short already-followed sequences when needed, and inserts explicit branches to already-emitted code.
- `patch` resolves call/branch/return targets from symbols or PCs and connects `cond` pointers.
- `mkfwd` builds skip-forward links to speed PC-to-`Prog` lookup.
- `brloop` collapses branch chains while detecting loops.
- `undef` reports remaining unresolved external references.

Important details:
- `dodata` puts small data objects first to improve addressing via `REGSB`.
- Data and BSS sizes are rounded to 8-byte boundaries.
- Undefined call targets can become dynamic imports via `SUNDEF`; non-call undefined branches are diagnosed.
- Branch target lookup uses `forwd` acceleration links created by `mkfwd`.
- `xfol` is inherited Plan 9 linker control-flow layout logic and mutates branch directions/links.

Filesystem relevance: indirect. It is binary layout and control-flow infrastructure, not filesystem logic.
