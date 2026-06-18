# File Research: sources/os/plan9/9front/sys/src/cmd/spin/pangen5.h

Generated template for minimized-automaton checkpoint write/read support under `MA` with `W_XPT` or `R_XPT`.

Key behavior:
- Defines buffered checkpoint I/O helpers `xwrite`, `xread`, and `wclose`.
- `w_xpoint` writes an `.xpt` checkpoint containing search counters, DFA depth, root/final/non-final vertices, and all layered DFA trees.
- Serializes vertices and edges by writing pointer identities as keys plus edge ranges and destination pointer values.
- `r_xpoint` reads an `.xpt` checkpoint, recreates temporary pointer-keyed trees, resolves edge destinations, reinserts vertices into the active DFA layers, and restores automaton statistics.
- `x_fixup`, `v_fix`, `v_insert`, `insert_withkey`, and `find_withkey` rebuild graph references after reading pointer identities from disk.
- `x_cpy_rev`, `x_tail`, `x_anytail`, `x_rm_stack`, and `x_remove` identify and remove stack states from the restored automaton, adjusting `nstates`.
- Provides consistency checks for checkpoint depth, buffer counts, missing vertices, duplicate inserts, and stack-state assumptions.

Dependencies:
- Requires the `MA` DFA implementation from `pangen4.h`, including `Vertex`, `Edge`, `layers`, `path`, `R`, `F`, `NF`, `dfa_store`, `dfa_member`, `insert_it`, `splay`, `new_vertex`, `new_edge`, and `recyc_vertex`.
- Uses generated/runtime globals `PanSource`, `MA`, `a_cycles`, `nstates`, `nlinks`, `truncs`, and `truncs2`.

Research notes:
- This is checkpoint/restart machinery for compressed-state searches.
- Because serialized graph references are based on original pointer identities, readback depends on a two-phase reconstruction and fixup pass rather than direct pointer reuse.
