<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/regedit_hexedit.c -->
# sources/user-network-fs/samba/source3/utils/regedit_hexedit.c

## Purpose

`regedit_hexedit.c` implements an ncurses hex editor widget used by registry value dialogs to view and edit binary data.

## Important APIs, Types, and Functions

`struct hexedit` tracks scroll offset, logical length, allocation size, cursor position, byte/nibble offsets, data buffer, and target window. Public functions are `hexedit_new()`, `hexedit_set_buf()`, `hexedit_get_buf()`, `hexedit_get_buf_len()`, `hexedit_set_cursor()`, `hexedit_refresh()`, `hexedit_driver()`, and `hexedit_resize_buffer()`. Internal helpers handle cursor movement, hex column mapping, editing, deletion, and scrolling.

## Control Flow

The widget renders 8 bytes per line as offset, two groups of hex bytes, and ASCII. `hexedit_driver()` maps abstract movement/delete commands or printable input to cursor movement and edit operations. Hex-column editing accepts only hex digits and updates one nibble at a time; ASCII-column editing writes the byte directly. Editing at `cursor_offset == len` grows the buffer by one. Backspace and delete remove bytes using `memmove()`.

## State and Persistence Behavior

All edited data is stored in the talloc-owned `data` buffer. Resizing can grow allocation exponentially, zero-fill new bytes, shrink logical length, or reset the cursor if it would move past the new end. The widget itself does not persist registry data; callers retrieve the buffer and write it through registry APIs.

## Dependencies and Integration Points

It depends on ncurses `WINDOW`, Samba `WERROR`, talloc allocation, and constants from `regedit_hexedit.h`. `regedit_dialog.c` wraps it as a dialog section and exposes resize/get/set operations to value editing.

## Risks and Edge Cases

`hexedit_set_buf()` allocates a zero-length array when size is zero; allocator behavior should be verified. Cursor math around line ends, ASCII/hex transitions, and deletion at boundaries is subtle. Page-up/page-down commands are defined but not implemented. `do_edit()` refreshes the whole widget after each edit, which is simple but can flicker on slow terminals.

## Test Signals

Widget tests should cover hex and ASCII entry, nibble replacement, append-at-end, backspace/delete at start/end/middle, shrink/grow resize, cursor movement across the gap between hex groups and ASCII, scrolling beyond one screen, zero-length buffers, and unimplemented page keys.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/regedit_hexedit.c -->
