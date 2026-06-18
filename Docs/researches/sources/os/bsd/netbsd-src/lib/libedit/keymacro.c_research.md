# File Research: sources/os/bsd/netbsd-src/lib/libedit/keymacro.c

## Purpose
Maintains libedit's extended-key and macro map. It maps multi-character key sequences to either editor commands (`XK_CMD`) or inserted strings/macros (`XK_STR`).

## Main Interfaces
- `keymacro_init`, `keymacro_end`, `keymacro_reset`: lifecycle for the keymacro buffer and trie.
- `keymacro_map_cmd`, `keymacro_map_str`: prepare temporary `keymacro_value_t` values for binding.
- `keymacro_get`: consumes input characters through `el_wgetc` to resolve a sequence.
- `keymacro_add`, `keymacro_delete`, `keymacro_clear`: mutate bindings.
- `keymacro_print`, `keymacro_kprint`, `keymacro__decode_str`: display bindings in printable form.

## Internal Design
The map is a sibling/child trie of `keymacro_node_t`. Each node stores a character, node type, value, child pointer for the next sequence character, and sibling pointer for alternate characters at the same depth.

A key sequence cannot be both a complete binding and a prefix of another binding. Adding a shorter sequence deletes longer bindings below it. Deleting recursively prunes empty parent nodes.

## Integration
`read_getcmd` in `read.c` calls `keymacro_get` when the active key map returns `ED_SEQUENCE_LEAD_IN`. `map_bind` in `map.c` calls the add/delete/print functions for user `bind` commands and terminal arrow-key bindings.

## Risks And Notes
- Prefix collisions are intentional but destructive: binding `abc` removes previous `abcd`-style bindings.
- The lookup path may consume characters while probing a sequence, so failed or partial matches affect input flow.
- String values are duplicated into trie nodes and freed by node teardown; callers should not assume retained ownership of temporary map values.
