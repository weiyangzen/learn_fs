# File Research: sources/os/plan9/9front/sys/src/cmd/2l/pass.c

This file implements major post-parse linker passes for `2l`: data/BSS layout, branch resolution and code following, stack-offset repair, numeric parsing, and undefined-symbol reporting.

Key routines:
- `dodata()` validates data initializers, packs small data symbols first, lays out remaining data, optionally pads/shuffles BSS under debug `j`, then assigns BSS offsets and defines `bdata`, `edata`, and `end`.
- `brchain()` follows chains of unconditional `ABRA` branches up to a fixed depth.
- `follow()` builds a new instruction order by calling `xfol(textp)`, initializes `BCASE` data symbols, and seeds per-instruction `stkoff`.
- `xfol()` performs branch-following layout, marks reachable code, copies short instruction runs to avoid branches, inverts conditional branches where useful, and inserts synthetic `ABRA` nodes.
- `relinv()` maps branch opcodes to their inverse condition, including floating branch conditions.
- `patch()` builds forward links, resolves `ABSR`/`ARTS` symbol references, maps `D_BRANCH` offsets to target `Prog` nodes, and collapses branch loops with `brloop()`.
- `mkfwd()` creates logarithmic-ish forward skip links for faster PC-to-`Prog` lookup.
- `dostkoff()` tracks logical stack offsets, inserts `AADJSP` instructions at function entry and control-flow joins, rewrites `D_AUTO`/`D_PARAM` offsets, and repairs returns with outstanding stack adjustment.
- `atolwhex()` parses signed decimal, octal, and hex constants.
- `undef()` emits diagnostics for unresolved `SXREF` symbols.

Dependencies and interactions:
- Uses global linker state from `l.h`: symbol hash table, `datap`, `textp`, `firstp`, `lastp`, `optab`, debug flags, and address constants.
- Feeds `span.c`: branch targets, instruction order, stack offsets, and symbol data layout are prerequisites for instruction sizing and output.

Research relevance:
- This is core linker control-flow and data-layout machinery. Changes here affect binary layout, stack metadata, branch target validity, and symbol addresses.

Risk notes:
- `xfol()` rewrites control flow destructively; branch inversion and instruction copying depend on exact opcode semantics.
- `dostkoff()` assumes stack effects from `optab`; incorrect `srcsp`/`dstsp` values propagate into bad auto/param addresses.
- `patch()` uses symbol `exit` as fallback for undefined calls/returns, so diagnostics may still leave a patched branch target.
