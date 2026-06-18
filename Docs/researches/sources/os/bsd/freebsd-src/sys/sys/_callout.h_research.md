# File Research: sources/os/bsd/freebsd-src/sys/sys/_callout.h

Core callout timer structure definitions.

Defines:
- Queue heads for `callout` in list, slist, and tailq forms.
- `callout_func_t(void *)`.
- `struct callout` fields for queue linkage, scheduled time, precision, argument, callback, associated lock object, public/internal flags, and target CPU.

Research relevance:
- Foundational kernel timer/callback data layout shared by timeout scheduling code.
