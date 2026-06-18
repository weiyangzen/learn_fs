# File Research: sources/os/plan9/9front/sys/src/cmd/6c/peep.c

- Role: Peephole and local copy-propagation optimizer over 6c `Reg` control-flow nodes.
- `peep()` first completes the `Reg` graph for instructions not represented in earlier allocator passes, then repeatedly applies local transformations.
- Optimizations include redundant MOV elimination, register substitution, collapsing repeated sign/zero extension moves, converting load-after-LEA patterns, rewriting `ADD/SUB ±1` to `INC/DEC` when flags are not needed, and deleting redundant compare-with-zero after flag-setting operations.
- `needc()` conservatively detects whether carry-sensitive later instructions prevent arithmetic-to-inc/dec rewrites.
- `uniqp()` and `uniqs()` identify unique predecessor/successor paths for safe local reasoning.
- `subprop()` attempts backward register substitution to enable later copy elimination.
- `copyprop()`, `copy1()`, and `copyu()` implement flow-sensitive copy propagation with instruction-specific use/set/read-alter-write classification.
- `copyas()`, `copyau()`, and `copysub()` compare and substitute direct/indirect register or stack references.
- `storeprop()` exists for local-variable load reuse after stores but is disabled by `if(0)`.
