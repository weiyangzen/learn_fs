# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/lua/llex.h

## Role

`llex.h` defines token IDs, token semantic payloads, and lexer state.

## Main Responsibilities

- Defines `FIRST_RESERVED`, reserved-word/token enum values, and `NUM_RESERVED`.
- Defines `SemInfo` for numeric and string token values.
- Defines `Token` and `LexState`, including current character, line counters, current/lookahead tokens, parser function state, stream, buffer, dynamic parser data, source, environment name, and decimal point.
- Declares lexer initialization, input setup, string interning, token advance/lookahead, syntax error, and token-to-string helpers.

## Integration Points

Shared between the lexer, parser, and code generator.

## Risk Notes

The enum order is coupled to `luaX_tokens` and reserved-word initialization. Changes require coordinated updates.
