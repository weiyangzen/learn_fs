# File Research: sources/os/bsd/netbsd-src/lib/libedit/keymacro.h

## Purpose
Declares the private keymacro data structures and functions shared by libedit internals.

## Main Declarations
- `keymacro_value_t`: union storing either an `el_action_t` command or a wide string.
- `keymacro_node_t`: opaque trie node type.
- `el_keymacro_t`: per-`EditLine` keymacro state with a print buffer, trie root, and local conversion value.
- Node type constants: `XK_CMD`, `XK_STR`, `XK_NOD`.

## Integration
Included by `el.h` users that need access to `EditLine`'s `el_keymacro` member. The declared functions are consumed by `map.c` and `read.c`.

## Risks And Notes
This is a private header. The trie layout is intentionally hidden; callers must use `keymacro_*` helpers rather than manipulating nodes directly.
