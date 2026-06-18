# sources/test-tools/kdevops/scripts/kconfig/lxdialog/checklist.c

## Purpose
This lxdialog file implements the checklist/radiolist widget used by menuconfig to select one option from a list and optionally request help.

## Important APIs, Types, And Functions
The public function is `dialog_checklist()`. Internal helpers `print_item()`, `print_arrows()`, and `print_buttons()` render list rows, scroll indicators, and Select/Help buttons. It uses the shared item-list API and global `dlg` color/attribute state from `dialog.h` and `util.c`.

## Control Flow
The function selects an initial item, verifies terminal dimensions, creates a centered dialog and list subwindow, computes checkbox/item positions, renders visible rows, then loops on keyboard input. Movement keys update `choice` and `scroll`; selection keys clear all item selections and mark the current item; Help returns button 1; resize recreates the windows; ESC uses the common escape filter.

## State And Persistence
All persistent UI state lives in the shared item list selection flags. Local layout state is static for the current module. No disk state is touched.

## Dependencies And Integration Points
It is linked into `mconf` through the Makefile's `lxdialog` object list. Return values are consumed by menuconfig's control logic.

## Risks And Test Signals
The source duplicates the top-level `kconfig/checklist.c`, so fixes must stay synchronized. Unchecked allocation and truncation behavior mirror the other copy. Test with curses-driven key sequences for scrolling, selection, help, resize, too-small terminal, and tagged separator items.
