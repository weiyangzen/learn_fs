# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/unixhead.mak

Early common Unix makefile fragment.

Key points:
- Sets `PLATFORM=unix_`.
- Defines command/object/executable syntax for Unix: object suffix `o`, empty executable suffix, `-c`, `-D`, `-I`, `-o`.
- Defines path separator `/`, shell `/bin/sh`, and generic commands `cat`, `cp`, and `rm -f`.
- Defines genconf argument forms for linker files.
- Sets compiler command aliases `CC_D` and `CC_INT`.
- Clears PC-specific assembler variables that would otherwise produce warnings.
- Defines default `std` target as `STDDIRS default`.

Dependencies and interactions:
- Included after compiler-specific options and before core `gs.mak`, `devs.mak`, and `contrib.mak`.
- Supplies basic syntax variables used by all subsequent make fragments.

Research relevance:
- This is the small but essential Unix syntax adapter for the old Ghostscript make system.
