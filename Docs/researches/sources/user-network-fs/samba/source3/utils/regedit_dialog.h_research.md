<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/regedit_dialog.h -->
# sources/user-network-fs/samba/source3/utils/regedit_dialog.h

## Purpose

`regedit_dialog.h` declares the dialog framework and high-level registry editor dialog API used by `regedit.c`.

## Important APIs, Types, and Functions

It defines `struct dialog`, `struct dialog_section`, `struct dialog_section_ops`, `enum dialog_action`, `enum section_justify`, button and option specs, and `enum dialog_type`. It declares section constructors for labels, separators, text fields, hex editors, buttons, and options; modal lifecycle functions; input/notice helpers; registry value edit/type selection dialogs; and search input.

## Control Flow

Consumers create a dialog, append sections, call `dialog_create()`, then run `dialog_modal_loop()` or use high-level wrappers such as `dialog_input()` and `dialog_edit_value()`. Section operation callbacks define how the modal input loop reacts to keys.

## State and Persistence Behavior

The public structs expose dialog internals: windows, panels, circular section list pointers, current focus, submit callback, and per-section ncurses windows. High-level edit functions can mutate registry values through the implementation.

## Dependencies and Integration Points

The header includes ncurses, panel, and menu headers, and forward-declares registry/value/search types. It is shared by the main editor, dialog implementation, and hex/value-list integration.

## Risks and Edge Cases

Because structs are public, other files can mutate internal pointers and break lifecycle assumptions. Callback contracts require callers to return `true` to close a submitted dialog and `false` to keep it open, which is easy to invert. Dialog dimensions are integer fields and negative widths have special meaning for expansion.

## Test Signals

Compile coverage plus UI integration tests should verify every declared constructor and high-level helper. ABI-sensitive checks should ensure public struct changes are reflected in all users and that callback semantics remain consistent.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/regedit_dialog.h -->
