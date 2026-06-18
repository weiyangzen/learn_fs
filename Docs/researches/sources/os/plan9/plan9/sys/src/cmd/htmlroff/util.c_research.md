# File Research: sources/os/plan9/plan9/sys/src/cmd/htmlroff/util.c

`util.c` provides allocation, formatting, warning, and rune literal helpers for htmlroff.

Key behavior:
- `emalloc`, `estrdup`, `erunestrdup`, `erealloc`, `esmprint`, and `erunesmprint` wrap allocation/formatting with fatal out-of-memory behavior.
- `warn` emits htmlroff diagnostics with current location `%L`.
- `L` converts C string literals to cached `Rune*` strings, keyed by source string pointer.

Important dependencies:
- Used across all htmlroff modules.

Notable risks/quirks:
- `L` assumes string literals can be identified by pointer identity and are immutable.
