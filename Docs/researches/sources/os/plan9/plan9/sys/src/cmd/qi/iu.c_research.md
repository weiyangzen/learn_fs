# File Research: sources/os/plan9/plan9/sys/src/cmd/qi/iu.c

Integer, logical, memory, special-register, trap, and cache/control instruction emulation for `qi`.

Key responsibilities:
- Defines the primary opcode 31 extended instruction table.
- Emulates integer arithmetic with carry, condition-code setting, comparisons, logical ops, rotates/masks, shifts, multiply/divide, CR/XER movement, SPR movement, and immediate forms.
- Emulates byte/half/word loads/stores, update/indexed variants, atomics, byte-reversal, string load/store, load/store multiple, and traps.
- Treats sync/cache operations mostly as traceable no-ops.
- Provides tracing for decoded instructions.

Dependencies:
- Uses `power.h`, memory accessors, floating indexed helpers, branch/syscall dispatch, XER/CR macros, and global register state.

Notable risks:
- Several comments mark overflow behavior as incomplete or approximate.
- `stwcx.` assumes reservation success.
- Some routines appear suspicious or intentionally rough for debugger use, such as byte-reversal and load/store-multiple register indexing.
- Privileged/control operations are largely unimplemented or no-op.
