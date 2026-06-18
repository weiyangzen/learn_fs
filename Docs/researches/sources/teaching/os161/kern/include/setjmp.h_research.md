# File Research: sources/teaching/os161/kern/include/setjmp.h

Declares kernel-level nonlocal jump support.

Key contents:
- Includes machine-dependent `jmp_buf` definition.
- Declares `setjmp` and `longjmp`.

Relevance:
- General kernel control-flow support; not used directly by the listed SFS/semfs files.
