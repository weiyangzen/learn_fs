# File Research: sources/os/plan9/9front/sys/src/cmd/wikifs/lookup.c

Tiny diagnostic program for wiki title lookup.

Key behavior:
- Includes the wiki support headers and prints `nametonum(argv[1])`.

Notable dependencies:
- Requires the wiki map machinery from `io.c` and global wiki directory setup from linked objects.

Research notes:
- No argument validation is present; it assumes a title argument exists.
