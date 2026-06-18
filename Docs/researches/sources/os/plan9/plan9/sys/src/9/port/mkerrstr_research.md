# File Research: sources/os/plan9/plan9/sys/src/9/port/mkerrstr

Purpose: Tiny rc/sed generator that converts `error.h` extern declarations into string definitions.

Key logic:
- Reads `../port/error.h`.
- Removes `extern`.
- Converts comments into assigned string literal values.

Dependencies and integration:
- Depends on the exact `error.h` declaration/comment shape.
