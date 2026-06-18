# File Research: sources/os/plan9/9front/sys/src/cmd/upas/filterkit/list.c

This command manages simple address allow/block lists backed by pattern files.

Key behavior:
- Usage: `list add|check patternfile [addressfile ...]`.
- Pattern file supports exact patterns prefixed by `=`, regex patterns prefixed by `~`, optional leading `!` for negative match, and `#include`.
- `simplify` lowercases addresses and generates an exact local match or a domain regex covering significant domain suffixes.
- `check` reads addresses, tests them against patterns, and exits nil on positive match, `!match` on only negative match, or `no match`.
- `add` appends simplified patterns for addresses not already matched and updates in-memory pattern state.
- Regexes are compiled on each check using Plan 9 regexp.

Integration and risks:
- Pattern parsing is line/token based and case-insensitive.
- `regerror` is stubbed to ignore regexp compilation errors, so bad regexes are silently skipped.
- Includes a hard-coded `.uk` domain depth special case.
