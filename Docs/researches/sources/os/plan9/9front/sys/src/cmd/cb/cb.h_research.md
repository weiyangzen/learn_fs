# File Research: sources/os/plan9/9front/sys/src/cmd/cb/cb.h

Purpose: Shared constants, tables, globals, macros, and prototypes for the `cb` C beautifier.

Key points:
- Defines keyword classes, operator spacing classes, boolean constants, parser-state constants, and buffer/stack sizes.
- Defines indentation stack structure `struct indent`.
- Defines `key[]` table for C keywords and declaration words.
- Defines `op[]` table for operators and spacing behavior.
- Declares and initializes global formatter state.
- Provides macros for output, indentation bumping, and whitespace consumption.
- Declares all helper functions implemented in `cb.c`.

Dependencies and interactions:
- Included by `cb.c`.
- Depends on `Biobuf` type from `<bio.h>` being included before it.

Research notes:
- This header contains definitions, not just declarations, so it is meant for a small single-program build rather than reuse across many translation units.
