# File Research: sources/os/plan9/9front/sys/src/cmd/spin/pangen4.h

Generated template for Spin’s minimized automaton (`MA`) storage backend.

Key behavior:
- Defines DFA data structures `Vertex` and `Edge`, with compact in-node edge slots plus overflow edge lists.
- Provides free-list recycling for edges and vertices.
- Implements transition/range operations: `Delta`, `cacheDelta`, `setDelta`, `numDelta`, edge insertion, edge copying, and edge/range coalescing.
- `dfa_init` builds an initial layered DFA with root, final, and non-final vertices.
- `dfa_store` inserts state-vector byte strings into the minimized automaton, performs path copying when shared nodes need splitting, finds reusable equivalent vertices, updates incoming counts, and recycles unreachable vertices.
- `dfa_member` tests membership by walking the byte string through the DFA.
- Maintains per-layer splay-tree indexes with `insert_it`, `find_it`, `delete_it`, `splay`, `mk_key`, `mk_special`, and equivalence checking through `checkit`.
- `dfa_stats` reports minimized automaton node/edge counts.

Dependencies:
- Included into generated verifier code under `#ifdef MA`.
- Uses generated/runtime symbols such as `nr_states`, `Uerror`, `emalloc`, and byte state-vector data.

Research notes:
- This is a specialized compressed state storage implementation, not normal Spin front-end logic.
- Pointer values are part of hashing/keying, so checkpoint/restart code in `pangen5.h` has to reconstruct pointer-linked graph structure carefully.
