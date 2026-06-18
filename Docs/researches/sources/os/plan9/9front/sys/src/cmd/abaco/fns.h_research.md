# File Research: sources/os/plan9/9front/sys/src/cmd/abaco/fns.h

Shared Abaco helper prototypes and rune convenience macros.

Key contents:
- Defines `runemalloc`, `runerealloc`, `runemove`, `hasbrk`, and `istrue`.
- Declares functions for plumbing, snarf, table layout, timers, command execution, search, scrolling, font/color utilities, URL composition, refresh, image loading, forms, layout lookup, and window creation.

Role:
- Complements `dat.h` with cross-file function declarations.

Notable risks:
- Macro wrappers do no overflow checking on rune counts.
