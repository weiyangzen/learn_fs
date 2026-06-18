# File Research: sources/os/plan9/plan9/sys/src/cmd/8l/pass.c

Purpose: linker transformation passes before final instruction sizing.

Key behavior: `dodata` lays out SDATA/SBSS and defines `bdata`, `edata`, `end`. `patch` resolves call/branch destinations and undefined calls. `follow`/`xfol` reorder basic blocks and invert branches to reduce jumps. `dostkoff` inserts stack adjustments and rewrites auto/param offsets. Also handles branch-chain compression, numeric parsing, imports, exports, and dynamic export table data synthesis.

Integration notes: runs between object loading and `span`. Stack adjustment pseudo-op `AADJSP` is later rewritten by `span`. Data layout directly controls `INITDAT`-relative addresses emitted by `asm.c`.
