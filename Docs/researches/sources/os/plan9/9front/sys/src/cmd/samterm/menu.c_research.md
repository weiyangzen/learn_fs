# File Research: sources/os/plan9/9front/sys/src/cmd/samterm/menu.c

`menu.c` implements samterm's button-2 and button-3 menus and the file menu state.

Button-2 actions include cut, paste, snarf, plumb, look, snarf exchange with rio, search/send, and host-defined custom menu commands. Entries are parenthesized when disabled by host/file lock.

Button-3 actions include new, zerox, resize, close, write, and file selection/opening from the file menu. Interactive actions use the bullseye cursor and mouse rectangle/window selection.

The file menu arrays (`name`, `text`, `tag`) track display names, bound `Text*`, and host tags. `menuins`, `menudel`, `whichmenu`, `setmenuhit`, and `genmenu3` maintain sorted menu display with modified/open/current markers and width-aligned names.

`sweeptext` creates a new `Text` and first `Flayer` for a new file or existing host tag, initializes its rasp, and sends the appropriate start message.

`menucmd` maintains custom `M` commands, toggling duplicate entries and emitting a command-list response when requested.
