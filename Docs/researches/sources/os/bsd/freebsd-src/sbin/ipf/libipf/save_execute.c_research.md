# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/save_execute.c

`ipmon` saver backend that pipes log messages to an external command.

Key behavior:
- Registers `executesaver`.
- Parses a command path/string.
- `execute_send()` opens the command with `popen(..., "w")`, writes the formatted message, and closes it.

Research notes:
- Executes a shell command for each message; command string trust is entirely caller/configuration dependent.
