# sources/test-tools/kdevops/scripts/kconfig/lxdialog/yesno.c

## Purpose
`yesno.c` implements a simple two-button confirmation dialog for menuconfig.

## Important APIs, Types, And Functions
The exported function is `dialog_yesno(title, prompt, height, width)`. `print_buttons()` renders Yes and No buttons using common button drawing.

## Control Flow
The function validates terminal size, centers and draws a dialog, prints title and prompt, renders buttons, and loops on input. `y` returns 0, `n` returns 1, Tab/left/right toggles the active button, Enter/Space returns the selected button, ESC uses the common handler, and resize recreates the dialog.

## State And Persistence
Only local `button` and `key` state is used. No persistent state or global item list is changed.

## Dependencies And Integration Points
It depends on ncurses and lxdialog utilities. Callers interpret 0 as Yes and 1 as No, with ESC/error codes passed through.

## Risks And Test Signals
The return convention is positional rather than symbolic, so callers must stay aligned. Tests should cover y/n shortcuts, button toggling, Enter/Space selection, ESC, resize, and too-small terminals.
