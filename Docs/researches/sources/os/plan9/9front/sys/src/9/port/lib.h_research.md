# File Research: sources/os/plan9/9front/sys/src/9/port/lib.h

Kernel-visible subset of libc declarations, formatting definitions, syscall constants, and core public structs.

Key contents:
- Defines `nelem`, `offsetof`, and kernel `assert`.
- Declares memory, string, UTF/rune, random, formatting, conversion, tokenization, and sorting helpers.
- Defines `Fmt` and vararg format checking pragmas.
- Defines Plan 9 mount/open/note constants.
- Defines `Qid`, `Dir`, old `OWaitmsg`, and `Waitmsg`.
- Defines Qid and Dir permission/type bits.

Role:
- Provides libc-like APIs to portable kernel C files without exposing full user libc.
- Supplies shared userspace/kernel ABI structs and constants used throughout the port layer.

Notable constraints:
- Some prototypes use older Plan 9 pointer types without `const`.
- The file intentionally aggregates declarations for code linked “complete, from libc.”
