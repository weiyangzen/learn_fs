# sources/sync-backup/rsync/zlib/inftrees.h

Purpose: private interface for inflate decode-table construction and representation.

Important APIs/types/functions: defines `code`, a four-byte table entry with `op`, `bits`, and `val`. Documents `op` encodings for literals, table links, length/distance bases with extra bits, end-of-block, and invalid-code markers. Defines sizing constants `ENOUGH_LENS`, `ENOUGH_DISTS`, and `ENOUGH`, plus enum `codetype` values `CODES`, `LENS`, and `DISTS`. Declares `inflate_table`.

Control flow: no runtime logic in the header, but the `code` layout drives decoder control flow. `inflate.c` and `inffast.c` inspect `op` bits to decide whether to emit a literal, follow a second-level table, read extra bits, end a block, or report invalid input.

State and persistence: no mutable state. The constants determine the size of `inflate_state.codes`, which persists between calls while a dynamic block is active.

Dependencies and integration points: included by `inflate.c`, `inflate.h`, `inffast.c`, `inffixed.h` through include context, and `inftrees.c`. The comments explicitly tie `ENOUGH_*` to exhaustive searches and to the root table sizes used in inflate calls (`9` for literal/length and `6` for distance dynamic tables).

Risks: changing `code` packing, `op` encoding, or `ENOUGH` sizes requires coordinated decoder/table-builder updates. Under-sizing `ENOUGH` can corrupt memory; over-sizing affects per-stream memory. The comment contains a typo in "distribution", but it has no behavior impact.

Test signals: compile-time size/layout assumptions should be checked across compilers. Dynamic-block fuzzing and maximum-table test vectors validate the constants and `op` interpretation.
