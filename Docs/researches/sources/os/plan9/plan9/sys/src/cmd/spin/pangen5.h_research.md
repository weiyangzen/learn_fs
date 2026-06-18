# File Research: sources/os/plan9/plan9/sys/src/cmd/spin/pangen5.h

This header embeds optional checkpoint read/write support for minimized automaton (`MA`) state storage.

Key contents:
- `Xpt[]`: generated code enabled by `MA` plus `W_XPT` or `R_XPT`.
- Buffered checkpoint output helpers `xwrite()` and `wclose()`.
- Serialization routines `w_vertex()`, `w_layer()`, and `w_xpoint()` for writing DFA layers to `<PanSource>.xpt`.
- Buffered input helper `xread()` plus reconstruction routines `r_layer()`, `v_fix()`, `v_insert()`, `x_fixup()`, and `r_xpoint()`.
- Stack-state removal routines `x_remove()`, `x_rm_stack()`, `x_tail()`, `x_anytail()`, and `x_cpy_rev()`.

Important details:
- The checkpoint stores statistics (`nstates`, `truncs`, `truncs2`, `nlinks`), DFA depth, root/final/non-final vertex identities, and every layer tree.
- The file format writes raw pointer values as temporary keys, then rebuilds pointer relationships through `find_withkey()` and `v_fix()`.
- `r_xpoint()` validates `dfa_depth == MA + a_cycles`.
- After loading, the code reconstructs layers, removes stored stack states, adjusts `nstates`, and reports how many stack states were removed.
- Uses fixed 4096-byte read/write buffers and low-level `creat`, `open`, `read`, `write`, and `close`.

Filesystem relevance:
- Direct but tooling-oriented: generated verifiers can persist and reload minimized-automaton checkpoints in `<model>.xpt` files.
