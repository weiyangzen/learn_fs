# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/kern/error.h

Declares the global error strings defined in `error.c`.

Role:
- Lets device and kernel code refer to shared error constants as extern `char[]`.
- Keeps error spellings centralized while allowing direct pointer/string use in `error()` and comparisons.

Notable detail:
- Comments mirror the human-readable meaning of each error constant.
