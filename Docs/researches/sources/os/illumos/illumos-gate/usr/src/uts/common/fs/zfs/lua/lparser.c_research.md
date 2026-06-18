# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/lua/lparser.c

## Purpose

Implements the Lua 5.2 parser and bytecode-generation front end for the ZFS-embedded Lua runtime. It consumes tokens from `llex`, builds `Proto` objects, manages lexical scopes/upvalues/goto labels, and emits VM instructions through `lcode`.

## Main Entry Point

- `luaY_parser(lua_State *L, ZIO *z, Mbuffer *buff, Dyndata *dyd, const char *name, int firstchar)`: creates the top-level closure/prototype, initializes lexical input, parses the main function, and returns the closure anchored on the Lua stack.

## Core Behavior

- Tracks function compilation with `FuncState`: current `Proto`, constants table, active blocks, bytecode PC, active locals, upvalues, and register allocation.
- Tracks parser dynamic state with `Dyndata`: active locals, pending gotos, and visible labels.
- Implements Lua grammar for expressions, table constructors, function definitions/calls, assignments, `if`, `while`, `repeat`, numeric/generic `for`, `do`, `local`, labels, `goto`, `break`, and `return`.
- Resolves names as locals, upvalues, or `_ENV` indexed globals.
- Handles closure creation by adding child prototypes to the parent and emitting `OP_CLOSURE`.
- Enforces parser limits including `MAXVARS`, `MAXUPVAL`, bytecode argument limits, and recursive C-call depth.
- Handles assignment conflicts where a later local/upvalue assignment would invalidate earlier table assignment operands.
- Implements Lua 5.2 label/goto rules, including prevention of jumping into local variable scope and generation of close instructions when gotos leave upvalue-owning scopes.

## Dependencies

- Lexer/token APIs: `llex.h`.
- Bytecode emission and patching: `lcode.h`, `lopcodes.h`.
- Runtime object model: `lobject.h`, `lfunc.h`, `lstate.h`, `lstring.h`, `ltable.h`.
- Error reporting and GC barriers: `ldebug.h`, `ldo.h`, `lmem.h`.

## Risks And Notes

- Scope and goto handling is the most error-prone area: `closegoto`, `findlabel`, `movegotosout`, and `leaveblock` must preserve Lua’s no-jump-into-scope rule and close upvalues on exits.
- Register allocation depends on the invariant `freereg >= nactvar`; each statement resets temporary registers after code generation.
- `anchor_token` protects token strings across function closure finalization and GC.
- The main chunk is always vararg and receives `_ENV` as its sole upvalue.
