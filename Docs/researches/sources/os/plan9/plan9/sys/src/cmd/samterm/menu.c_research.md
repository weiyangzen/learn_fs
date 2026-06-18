# File Research: sources/os/plan9/plan9/sys/src/cmd/samterm/menu.c

Implements `samterm` button-2 and button-3 menus plus the terminal file-name list.

Key responsibilities:
- Global arrays `name`, `text`, and `tag` maintain menu entries and associated `Text` objects.
- `menu2hit` handles cut, paste, snarf, plumb, look, exchange/send, and search.
- `menu3hit` handles new, zerox, resize, close, and write.
- `sweeptext` creates a new window by mouse rectangle selection.
- `menuins`, `menudel`, and `whichmenu` maintain menu entries.
- `setpat`, `paren`, `genmenu2`, `genmenu2c`, and `genmenu3` generate dynamic menu labels.

Behavior notes:
- Menu entries are decorated with dirty-state prefixes and parenthesized when no live text window is attached.
- The command menu uses `Send` where file windows use `Search`.
- Plumb menu is disabled when protocol version or plumb fd does not support it.
