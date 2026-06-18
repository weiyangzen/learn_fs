# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/ichar.h

Declares shared character rendering operator support.

Key points:
- Documents execution-stack layout used by character rendering operators.
- Defines `snumpush` as 9 and macros for retrieving text enumerator, procedure slot, saved stack depths, saved gstate level, saved font/root font, and completion procedure from the execution stack.
- Declares show setup, continuation, dispatch, cleanup, glyph ref creation, and `stringwidth` finish helpers.
- Declares cachedevice operators and width-only show query.

Research notes:
- Character rendering in the interpreter is continuation-based through the execution stack.
- The macros encode a fixed stack-frame ABI shared by `zchar*.c`.
