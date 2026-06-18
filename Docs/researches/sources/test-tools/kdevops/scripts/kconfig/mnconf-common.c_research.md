# sources/test-tools/kdevops/scripts/kconfig/mnconf-common.c

## Purpose
`mnconf-common.c` provides shared search-result jump-key behavior for the `mconf` and `nconf` Kconfig UIs. It cycles numeric jump labels from `1` through `9` and maps numeric key presses in visible search result ranges back to menu targets.

## Important APIs, Types, And Functions
Exports are `next_jump_key(int key)`, `handle_search_keys(int key, size_t start, size_t end, void *data)`, `get_jump_key_char(void)`, and global `int jump_key_char`. It uses `struct search_data` and `struct jump_key` from Kconfig headers/list types.

## Control Flow
`next_jump_key()` normalizes non-numeric or out-of-range input to `'1'`, increments numeric keys, and wraps after `'9'`. `get_jump_key_char()` advances the global jump key and returns it. `handle_search_keys()` rejects non-numeric input, then walks `data->head`, assigns the same cyclic index sequence used for rendering, ignores jump offsets before the current viewport, stops at offsets after the viewport, and fills `data->target` when the pressed key matches.

## State And Persistence
Only `jump_key_char` is global process state. Search callers reset it to zero before rendering a result page. There is no persistence beyond process memory.

## Dependencies And Integration Points
Depends on `list.h`, `expr.h`, and `mnconf-common.h`. `menu.c` calls `get_jump_key_char()` while formatting search relation text. `mconf.c` and `nconf.c` call `handle_search_keys()` from scrollable search result dialogs.

## Risks And Edge Cases
The key labels repeat every nine visible jump targets, so ambiguous labels can occur in large result sets. Correctness depends on the offsets recorded in `get_prompt_str()` matching the text window viewport byte offsets passed by each UI.

## Test Signals
Search for a term with more than nine visible locations, scroll result windows, press numeric jump keys, and confirm the target menu opens only for locations visible in the current viewport.
