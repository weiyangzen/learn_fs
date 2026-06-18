# File Research: sources/os/plan9/plan9/sys/src/cmd/plumb/match.c

Rule matching and action startup for plumber messages.

Key responsibilities:
- Implements verbs `is`, `matches`, `isfile`, `isdir`, `set`, `add`, and `delete`.
- Tracks regex capture variables `$0` through `$9`.
- Handles click-aware matching on message data.
- Rewrites clicked messages by removing `click` and optionally replacing data with matched text.
- Builds argv vectors from expanded action strings.
- Starts external clients/actions with `proccreate()` and `procexec()`.
- Determines when messages should be held for a client port.

Important behavior:
- `matches` requires full-string matches except click matching, where the regex match must span the clicked character.
- `isfile`/`isdir` resolve relative paths against message `wdir`.
- If a ruleset has a port and the message has no destination, matching assigns that port.
- `plumb client` actions set `holdforclient`.

Dependencies:
- Uses Plan 9 regexp, plumb attributes, `expand()` from `rules.c`, and filesystem `dirstat`.

Notable risks:
- `verbis()` calls `strcmp()` on fields that are expected non-nil; malformed messages could crash if fields are nil.
- `buildargv()` uses whitespace tokenization plus single-quote processing from `expand()`, not full shell parsing.
