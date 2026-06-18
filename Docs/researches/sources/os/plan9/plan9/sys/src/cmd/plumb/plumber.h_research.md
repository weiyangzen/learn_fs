# File Research: sources/os/plan9/plan9/sys/src/cmd/plumb/plumber.h

Shared plumber rule, execution, and global declarations.

Key responsibilities:
- Defines rule objects (`data`, `dst`, `src`, `type`, `wdir`, `attr`, `arg`, `plumb`).
- Defines verbs (`is`, `matches`, `isfile`, `isdir`, `set`, `add`, `delete`, `to`, `start`, `client`).
- Declares `Rule`, `Ruleset`, and `Exec`.
- Declares cross-file functions for parsing, matching, expansion, startup, filesystem service, and rule writing.
- Declares global rule/user/home/port state.

Important behavior:
- `Exec` stores regex matches, clicked-span state, derived file/dir paths, and hold-for-client state.
