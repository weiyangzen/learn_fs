# File Research: sources/os/bsd/netbsd-src/lib/libedit/readline.c

## Purpose
Implements a GNU Readline compatibility layer on top of libedit. It exposes readline-style global variables, line-reading functions, completion hooks, history expansion, and history-list APIs.

## Main Public Surface
Includes:
- Initialization and input: `rl_initialize`, `readline`, `rl_set_prompt`, `rl_read_key`, callback-mode helpers, redisplay helpers.
- History: `using_history`, `add_history`, `remove_history`, `replace_history_entry`, `clear_history`, `history_get`, `history_list`, `read_history`, `write_history`, `append_history`, `history_truncate_file`, search/position helpers.
- Expansion/tokenizing: `history_expand`, `get_history_event`, `history_arg_extract`, `history_tokenize`.
- Completion: `rl_complete`, `rl_completion_matches`, `rl_display_match_list`, filename/user completion wrappers.
- Compatibility stubs or partial implementations for keymaps, signal cleanup, kill functions, and miscellaneous readline APIs.

## Global State
The file defines readline-compatible globals such as `rl_line_buffer`, `rl_point`, `rl_end`, prompt/completion hooks, stream pointers, history counters, completion behavior flags, signal flags, and `rl_readline_state`. Internally it owns static `History *h`, `EditLine *e`, a 256-entry readline command map, and buffers for history list compatibility.

## Initialization Flow
`rl_initialize` recreates the underlying `EditLine` and `History`, configures streams, disables edit mode when echo is off, wires history through `EL_HIST`, installs resize and getc hooks, sets prompt handling with readline ignore markers, sets Emacs mode, sources config, binds readline-compatible keys, and installs completion/suspend adapter functions.

## History Compatibility
Readline history functions translate between readline's oldest-based offsets and libedit's event/cursor model. They store optional `histdata_t` through libedit's event data extensions (`H_NEXT_EVDATA`, `H_DELDATA`, `H_REPLACE`). File persistence delegates to `history.c`.

## Completion Compatibility
Completion honors readline globals and hooks, builds match vectors, displays lists, supports append characters, and maps tab to the internal `_el_rl_complete` adapter.

## Risks And Notes
- This layer is highly global and not reentrant; one static `EditLine`/`History` instance backs the exported API.
- Several GNU Readline APIs are present as compatibility stubs or reduced implementations.
- History offset direction differs between readline and editline, so position/search functions are sensitive to off-by-one errors.
- Applications may directly inspect `rl_line_buffer`, `rl_point`, and `rl_end`; `_rl_update_pos` and resize hooks keep those globals synchronized.
