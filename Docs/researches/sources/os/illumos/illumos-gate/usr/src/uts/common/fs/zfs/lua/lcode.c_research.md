# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/lua/lcode.c

## Role

`lcode.c` is the Lua bytecode generator. It converts parser expression state into VM instructions, manages registers and constants, patches jumps, folds constants, and emits opcodes for expressions, control flow, assignments, calls, and table constructors.

## Main Responsibilities

- Emits `Instruction` values into a function prototype and maintains matching line-number metadata.
- Manages register allocation, stack-size limits, and expression placement into registers or RK operands.
- Builds and patches jump lists for boolean expressions, control flow, close-upvalue jumps, and labels.
- Deduplicates constants in the function constant table, including special handling for `-0` and NaN numeric constants.
- Emits loads, stores, table indexing, method calls, returns, varargs, concatenation, arithmetic, comparisons, unary operators, and table constructor `SETLIST` batches.
- Optimizes adjacent `LOADNIL` operations and chained concatenations.

## Local/ZFS Adaptation

Constant folding includes a patch that refuses to fold `INT64_MIN / -1`, avoiding an overflow/undefined arithmetic edge case in this integer-oriented embedding.

## Risk Notes

The most sensitive invariants are jump offsets, register lifetimes, constant-table indexing, RK operand limits, and `pc`/lineinfo synchronization. A wrong patch or missing register free can produce invalid bytecode that fails later in the VM rather than at parse time.
