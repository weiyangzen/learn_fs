# sources/test-tools/kdevops/scripts/kconfig/lxdialog/inputbox.c

## Purpose
`inputbox.c` implements a menuconfig text input dialog, used for editing string, int, or hex configuration values from the curses frontend.

## Important APIs, Types, And Functions
It defines global `dialog_input_result[MAX_LEN + 1]` and exports `dialog_inputbox(title, prompt, height, width, init)`. `print_buttons()` renders Ok and Help buttons.

## Control Flow
The dialog copies the initial value into `dialog_input_result`, validates terminal size, draws the prompt and input field, displays a horizontally scrolled view when the string exceeds field width, and enters a key loop. When the input field is active, printable keys insert at the cursor, backspace deletes, and left/right move or scroll. Tab/up/down/left/right cycle focus between input, Ok, and Help. Enter or Space returns the focused action; `o` and `h` are shortcuts; resize recreates the window.

## State And Persistence
The edited value persists in the global `dialog_input_result` buffer after return. Local state tracks cursor position, visible offset, length, and active button. No files are written.

## Dependencies And Integration Points
It uses ncurses and common drawing/helpers from `dialog.h`/`util.c`. Menuconfig reads `dialog_input_result` after a successful return.

## Risks And Test Signals
`strcpy(instr, init)` can overflow if the caller passes an initial value longer than `MAX_LEN`. Editing is byte-oriented and not multibyte-aware. Tests should cover long initial values, insertion/deletion in the middle, horizontal scrolling, focus cycling, Help return, ESC, and resize.
