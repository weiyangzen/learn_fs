# File Research: sources/os/plan9/plan9/sys/src/cmd/dial/expect.c

This file implements an expect-style helper for dial scripts.

Key behaviors:
- Usage: `expect [-q] [-t secs] goodstring [badstring ...]`.
- Reads from stdin into a sliding buffer sized to the longest target string plus 4096 bytes.
- Exits successfully when the good string appears.
- Exits with the matching bad string as status if any bad string appears first.
- Supports case-insensitive matching with `-i`.
- Mirrors input to `/dev/cons` unless `-q` is set.
- Default timeout is 5 minutes.

Notable implementation details:
- Keeps enough previous bytes to match strings crossing read boundaries.
- `writewithoutcr()` strips carriage returns before echoing.
- A `catch()` note handler is defined but not installed; timeout relies on Plan 9 alarm behavior if no notify handler is active.
