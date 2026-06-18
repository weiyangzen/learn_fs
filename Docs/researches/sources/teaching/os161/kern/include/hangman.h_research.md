# File Research: sources/teaching/os161/kern/include/hangman.h

Optional deadlock detector interface enabled by `options hangman`.

When enabled:
- Defines `struct hangman_actor` and `struct hangman_lockable`.
- Declares wait/acquire/release tracking hooks.
- Provides declaration and initialization macros for actors and lockables.

When disabled:
- All macros collapse to no-ops/empty declarations.

Relevance:
- `struct cpu` embeds `HANGMAN_ACTOR(c_hangman)` so CPU/thread synchronization can optionally participate in deadlock tracking.
