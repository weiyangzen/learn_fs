# File Research: sources/os/plan9/9front/sys/src/cmd/mk/shprint.c

Expands mk-controlled variables inside recipe text before shell execution or printing.

Key behavior:
- `shprint()` copies recipe text, expanding `$name` and `${name}` through `vexpand()`, while preserving quoted strings.
- Only expands internal variables and variables set by mkfiles/command line (`S_WESET`); inherited untouched environment variables remain `$name`.
- `front()` shortens long commands for error messages by keeping first fields and the last field.

Important dependencies: `mk.h`, `copyq`, `bufcpyw`, `symlook`, `shname`.

Notable risks:
- Expansion policy intentionally avoids expanding all environment variables; changing it would alter recipe shell behavior.
