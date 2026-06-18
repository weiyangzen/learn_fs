# File Research: sources/os/plan9/plan9/sys/src/cmd/eqn/e.h

Main shared header for `eqn`.

Key contents:
- Character classes and spacing matrix declaration.
- Debug/error macros and token/font constants.
- Global parser/layout state: point size, font stack, display mode, type setter, equation registers, heights, baselines, left/right fonts/classes, delimiters, and input stacks.
- Tables for keywords, definitions, reserved words, and tuning definitions.
- Input source, argument, and font-stack structs.
- Prototypes for parser helpers, input handling, symbol lookup, box constructors, font/size/motion operations, piles, matrices, and text conversion.

Filesystem relevance:
- No direct filesystem logic, but declares include-file input structures used by `eqn/include`.
