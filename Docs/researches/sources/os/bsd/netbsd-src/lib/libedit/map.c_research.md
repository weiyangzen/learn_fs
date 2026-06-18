# File Research: sources/os/bsd/netbsd-src/lib/libedit/map.c

## Purpose
Defines libedit's editor key maps and binding machinery. It provides default Emacs, vi insert, and vi command maps, plus runtime helpers to switch modes, bind keys, list bindings, and add custom editor functions.

## Main Interfaces
- `map_init`, `map_end`: allocate/copy key maps, function tables, help tables, and word-character state.
- `map_init_vi`, `map_init_emacs`: install vi or Emacs defaults.
- `map_set_editor`, `map_get_editor`: set/query editor mode.
- `map_set_wordchars`, `map_get_wordchars`: configure word-boundary behavior.
- `map_bind`: implements the user-visible `bind` command.
- `map_addfunc`: appends application-defined editor functions to the dispatch/help tables.

## Internal Data
Large static arrays define 256-entry default maps for Emacs, vi insert, and vi command mode. The active `EditLine` state keeps a normal map, alternate map, current map pointer, help table, function pointer table, mode type, and word character string.

## Binding Flow
`map_bind` parses flags:
- `-v` / `-e` switch editor defaults.
- `-a` targets the alternate map.
- `-s` binds a key sequence to a string.
- `-k` operates on terminal key names.
- `-r` removes a binding.
- `-l` lists editor function help.

Single-byte bindings update the selected map directly. Multi-character bindings go through `keymacro_add` and mark the first character as `ED_SEQUENCE_LEAD_IN`.

## Dependencies
Relies on generated `fcns.h`, `help.h`, and `func.h`, plus `parse.c`, `keymacro.c`, terminal helpers, and character encoding helpers.

## Risks And Notes
- Generated command-number ordering is central: key-map arrays, help entries, and function dispatch must agree.
- `map_addfunc` reallocates parallel arrays; allocation failure after one successful realloc can leave partial state.
- Multi-character binding semantics inherit the prefix limitations of `keymacro.c`.
