<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/regedit_hexedit.h -->
# sources/user-network-fs/samba/source3/utils/regedit_hexedit.h

## Purpose

`regedit_hexedit.h` declares the public interface and key constants for the ncurses hex editor widget used by registry dialogs.

## Important APIs, Types, and Functions

It defines abstract driver key constants such as `HE_CURSOR_UP`, `HE_CURSOR_DOWN`, `HE_BACKSPACE`, and `HE_DELETE`, sets `LINE_WIDTH` to 44, forward-declares `struct hexedit`, and declares buffer lifecycle, rendering, cursor, driver, and resize functions.

## Control Flow

Callers create a widget with `hexedit_new()`, set or replace the buffer with `hexedit_set_buf()`, render with `hexedit_refresh()`, route key events through `hexedit_driver()`, update the visible cursor with `hexedit_set_cursor()`, and retrieve the edited buffer before persisting it.

## State and Persistence Behavior

The widget owns an editable in-memory copy of binary data. Persistence is intentionally external: `regedit_dialog.c` reads the buffer and calls registry write helpers when the user submits a dialog.

## Dependencies and Integration Points

It includes ncurses for `WINDOW` and relies on Samba/talloc types from including translation units. The abstract key constants decouple dialog key handling from internal cursor logic.

## Risks and Edge Cases

The fixed `LINE_WIDTH` must stay consistent with the renderer's offset/hex/ASCII columns. Adding driver commands requires implementation in `hexedit_driver()`, not just new constants. Callers must not retain the returned buffer after freeing the widget.

## Test Signals

Compile coverage through `regedit_dialog.c` validates the interface. Runtime tests should verify the widget can be embedded in a curses subwindow, edited via abstract keys, resized, and harvested into a registry value blob without stale pointers.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/regedit_hexedit.h -->
