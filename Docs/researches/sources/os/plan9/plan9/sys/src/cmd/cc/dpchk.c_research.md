# File Research: sources/os/plan9/plan9/sys/src/cmd/cc/dpchk.c

This file implements Plan 9 compiler checks for `#pragma varargck` and related pragmas.

Key behavior:
- Builds format-flag classifications for vararg checking with `argflag()` and `getflag()`.
- Records known vararg functions and typed format verbs through `newname()` and `newprot()`.
- Parses `#pragma varargck argpos`, `type`, and `flag` forms in `pragvararg()`.
- Checks calls in `dpcheck()` by finding the declared format-string parameter and comparing actual arguments against registered format prototypes.
- Implements `#pragma pack`, `#pragma fpround`, `#pragma profile`, and `#pragma incomplete`.

Important details:
- Checks are gated by debug flag `F`; warnings are emitted only when enabled.
- Star width arguments must be `int` or `uint`.
- `#pragma incomplete` can mark struct/union types as deliberately incomplete or toggle debug `T`.

Filesystem relevance:
- Indirect. Provides compiler diagnostics and pragma controls.
