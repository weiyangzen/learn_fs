# File Research: sources/os/plan9/9front/sys/src/cmd/cpp/cpp.h

Shared declarations for the preprocessor. Defines token kinds, keyword kinds, token rows, source stack frames, macro symbol records, include tracking, and global state.

Important elements:
- `Token` carries type, flags, hideset index, whitespace length, token length, and text pointer.
- `Tokenrow` is the mutable token sequence abstraction used by lexer, expander, and output.
- `Source` tracks file/string input buffers and include nesting.
- `Nlist` stores macro values, arguments, keyword values, and flags.
- Constants bound preprocessor sizes: include dirs, `#pragma once` entries, macro args, input/output buffers, and `#if` depth.
