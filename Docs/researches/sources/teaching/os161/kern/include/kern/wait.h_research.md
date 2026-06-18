# File Research: sources/teaching/os161/kern/include/kern/wait.h

Defines wait/waitpid flags and wait-status encoding.

Key contents:
- Flags `WNOHANG`, `WUNTRACED`.
- Special wait pids `WAIT_ANY`, `WAIT_MYPGRP`.
- Encodes status in low two bits plus value payload.
- Provides `WIF*`, `W*STATUS`, and kernel `_MKWAIT_*` macros.

Relevance:
- Process ABI support; not directly related to filesystem code in this group.
