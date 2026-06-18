# File Research: sources/os/plan9/plan9/sys/src/cmd/ssh2/dial.c

This file provides a parallel Plan 9 `dial` implementation for non-threaded/process-style programs.

Key behavior:
- Parses dial strings of the form `[/net/]proto!dest`, including connection directories with numeric channel components.
- Talks to `/net*/cs` to translate a service into one or more clone/destination lines.
- Attempts multiple translated addresses in parallel using `rfork(RFPROC|RFMEM)`, taking the first successful connection.
- Falls back from `/net` to `/net.alt` unless the original failure was a connection refusal.
- Opens protocol clone files, writes `connect dest [local]`, opens the resulting `data` file, and optionally returns the ctl fd and connection directory.

Important details:
- Parent and children share the heap through `RFMEM`; `Conn`/`Dest` are allocated so the parent can observe child state.
- Outstanding child dials are interrupted with `postnote(..., "alarm")`.
- A two-minute alarm bounds parallel connection attempts when no caller alarm exists.
- Error reporting keeps a non-`does not exist` error as the best diagnostic.

Filesystem relevance:
- Direct: manually drives Plan 9 network filesystem control/data files under `/net`, `/net.alt`, and protocol clone directories.
