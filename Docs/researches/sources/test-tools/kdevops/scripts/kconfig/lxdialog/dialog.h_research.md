# sources/test-tools/kdevops/scripts/kconfig/lxdialog/dialog.h

## Purpose
`dialog.h` is the common lxdialog interface for menuconfig's ncurses widgets. It defines colors, global dialog state, item-list structures, minimum window sizes, key constants, and widget/drawing function prototypes.

## Important APIs, Types, And Functions
Important types are `struct dialog_color`, `struct subtitle_list`, `struct dialog_info`, `struct dialog_item`, and `struct dialog_list`. It declares global `dlg`, `dialog_input_result`, `saved_x`, and `saved_y`. It exposes item-list builders/accessors, common handlers `on_key_esc()` and `on_key_resize()`, initialization functions `init_dialog()`, `dialog_clear()`, `end_dialog()`, drawing helpers, and widget APIs `dialog_yesno()`, `dialog_msgbox()`, `dialog_textbox()`, `dialog_menu()`, `dialog_checklist()`, and `dialog_inputbox()`.

## Control Flow
The header has no runtime flow. Its macros and prototypes define how widget modules share state and return key/button codes.

## State And Persistence
It centralizes global ncurses state and the transient item list. There is no persistent storage.

## Dependencies And Integration Points
It includes POSIX headers and `ncurses.h`. All lxdialog C files include it, and menuconfig code uses the declared widget APIs.

## Risks And Test Signals
Global mutable state means widgets are not reentrant. `MAX_LEN` and `MAXITEMSTR` bound input/text and item display. Minimum-size constants affect resize behavior. Compile/link tests plus curses UI smoke tests cover this header.
