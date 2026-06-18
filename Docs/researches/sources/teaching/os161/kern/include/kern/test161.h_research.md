# File Research: sources/teaching/os161/kern/include/kern/test161.h

Defines test161 automated-testing support.

Key contents:
- Success/fail constants.
- Includes `kern/secret.h`.
- Progress macros print dots via `kprintf` in kernel or `printf` in userland.
- Loud progress always emits; testing progress emits only when `SECRET_TESTING` is defined.
- Declares success/secret-print/partial-credit helpers and kernel bootstrap hook.

Relevance:
- Test infrastructure, not directly filesystem logic.
