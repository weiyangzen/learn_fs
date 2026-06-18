# File Research: sources/os/plan9/9front/sys/src/cmd/qi/iu.c

Integer, logical, load/store, special-register, trap, and cache-control instruction handlers for `qi`.

Key responsibilities:
- Defines extended opcode group 31 table `op31`.
- Implements arithmetic with carry/overflow state: add/sub variants, multiply/divide, negate.
- Implements logical and rotate/mask operations: and/or/xor/nor/nand/eqv, rlwimi/rlwinm/rlwnm, shifts.
- Implements compares and condition-register updates.
- Implements loads/stores for bytes, halfwords, words, byte-reversed forms, string load/store, multiple load/store, and reservation approximations.
- Implements special register moves for XER/LR/CTR/TB/DEC and condition-register moves.
- Handles traps and no-op style control/cache instructions (`sync`, `icbi`, `dcb*`).

Dependencies and coupling:
- Uses instruction decode macros from `power.h`, memory accessors from `mem.c`, and trace/error globals.
- Calls floating indexed load/store handlers declared from `float.c`.

Notable behavior:
- Some semantics are approximate or buggy by comments, especially overflow and reservation behavior.
- Byte-reversal helpers appear suspicious: `lhbrx`/`sthbrx` duplicate low byte in both positions, and `stwbrx` writes from a zero local instead of `reg.r[rd]`.
