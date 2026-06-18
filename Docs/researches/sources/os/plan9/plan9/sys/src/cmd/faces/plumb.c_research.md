# File Research: sources/os/plan9/plan9/sys/src/cmd/faces/plumb.c

Handles mail event input and show-mail output for `faces`.

Key behavior:
- `initplumb()` opens `send` and `seemail` plumber ports; if `seemail` is unavailable, it tails `/sys/log/mail`.
- `showmail()` sends a plumb message telling mail tools to display a message path.
- `nextface()` returns the next new `Face`, processing plumb `new` and `delete` messages or log lines.
- Deduplicates messages by digest with `alreadyseen()`.
- Parses sender names into user/domain using `@` and `!` conventions.
- Parses mail log dates and upas/fs info files for startup loading.
- `dirface()` constructs a `Face` from a stored `/mail/fs` message `info` file.

Important implementation details:
- `maildirs` is a dynamic list of accepted mail roots.
- Log fallback recognizes both `delivered user From` and `remote local!user From` records.
- `tweakdate()` shortens display dates relative to the current day.

Risks and invariants:
- Fallback log tailing sleeps when no new data is available.
- `setname()` lowercases the sender buffer in place, so callers must pass owned mutable strings.
