# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/lua/lparser.h

## Purpose

Defines parser-facing data structures used by `lparser.c` and bytecode generation.

## Key Definitions

- `expkind`: expression forms such as constants, locals, upvalues, indexed expressions, jumps, relocatable instructions, calls, and varargs.
- `expdesc`: expression descriptor with kind-specific payload plus true/false jump patch lists.
- `Vardesc`: active local variable descriptor.
- `Labeldesc` and `Labellist`: label/goto tracking records.
- `Dyndata`: parser dynamic arrays for active locals, gotos, and labels.
- `FuncState`: compilation state for one Lua function/prototype.

## Public Interface

- `luaY_parser(...)`: parser entry point implemented in `lparser.c`.

## Dependencies

- `llimits.h`, `lobject.h`, and `lzio.h`.

## Risks And Notes

- The numeric sizes of `FuncState` fields are tied to Lua bytecode limits, especially `lu_byte` counts for active locals/upvalues/registers.
- `VINDEXED` stores table/index register-or-constant metadata compactly; misuse can generate invalid `OP_GETTABLE`/`OP_SETTABLE` operands.
