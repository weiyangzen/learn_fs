# File Research: sources/os/plan9/9front/sys/src/cmd/dtracy/act.c

This file converts parsed dtracy clauses into kernel-facing `DTClause`/`DTActGr` structures and parses trace records returned from the kernel. It owns global clause storage (`clause`, `clauses`, `nclauses`) and the enabled-probe lookup table keyed by epid.

Key responsibilities:
- Builds clauses from parser callbacks: `clausebegin`, `addprobe`, `addstat`, `addarg`, `addpred`, `clauseend`.
- Normalizes probe names with `insertstars`, filling empty probe tuple components with `*`.
- Prepares print/printf actions, including kernel trace actions for runtime values via `tracegen`.
- Allocates aggregation IDs, records aggregate metadata, and emits `ACTAGGKEY`/`ACTAGGVAL`.
- Packs generated clauses with `dtclpack`.
- Parses binary trace buffers, fault records, and record payloads through `unpack`, `parsebuf`, `parsefault`, `parseclause`, and `receval`.

Important implementation notes:
- `receval` re-evaluates record-side expressions against captured record fields, supporting variables like `time` and `probe`.
- String record extraction allocates a copy and has a TODO leak comment.
- `execprintf` manually constructs a vararg block, matching the rewritten format prepared by `prepprintf`.
- `dump` provides a detailed debug view of generated kernel bytecode and record formatting.
