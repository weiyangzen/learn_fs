# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/lua/lopcodes.c

## Role

`lopcodes.c` provides opcode names and opcode-mode metadata for the Lua VM.

## Main Responsibilities

- Defines `luaP_opnames`, mapping every opcode to a printable name.
- Defines `luaP_opmodes`, describing each opcode's instruction format, whether it is a test, whether it sets register A, and how B/C operands are interpreted.

## Integration Points

Code generation, debug symbolic execution, disassembly-style diagnostics, and the VM depend on these arrays matching the `OpCode` enum order in `lopcodes.h`.

## Risk Notes

The arrays are order-coupled to `OpCode`. Any opcode insertion, removal, or reorder must update this file atomically.
