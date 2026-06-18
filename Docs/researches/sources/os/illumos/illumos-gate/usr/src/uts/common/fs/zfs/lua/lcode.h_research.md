# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/lua/lcode.h

## Role

`lcode.h` declares the compiler code-generation API and expression operator enums.

## Main Responsibilities

- Defines `NO_JUMP`, binary operators, unary operators, and helpers for accessing generated instructions.
- Provides wrappers for emitting signed `sBx` jumps and multi-result expressions.
- Declares code emission, register reservation, constant creation, expression discharge, boolean jump handling, variable stores, prefix/infix/postfix operator generation, list construction, jump patching, and return generation functions.

## Integration Points

The parser consumes this header to emit VM bytecode into `Proto` objects. It ties together lexer/parser expression descriptors and `lopcodes.h` instruction formats.

## Risk Notes

The operator enum order is intentionally coupled to parser and opcode mapping. Reordering requires coordinated updates.
