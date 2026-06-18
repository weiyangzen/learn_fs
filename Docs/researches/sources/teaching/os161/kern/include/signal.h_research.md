# File Research: sources/teaching/os161/kern/include/signal.h

Kernel-facing signal header.

Key contents:
- Includes machine-dependent signal definitions from `<kern/machine/signal.h>`.
- Includes machine-independent signal ABI from `<kern/signal.h>`.

Relevance:
- Provides consolidated signal definitions for kernel code.
- No direct filesystem dependency in this group.
