<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/regedit_dialog.c -->
# sources/user-network-fs/samba/source3/utils/regedit_dialog.c

## Purpose

`regedit_dialog.c` implements the reusable ncurses dialog framework for `regedit`, plus higher-level dialogs for input prompts, notices, value editing, type selection, and search options.

## Important APIs, Types, and Functions

The core framework uses `struct dialog`, `struct dialog_section`, and `struct dialog_section_ops`. Section implementations include labels, horizontal separators, text fields, hex editors, buttons, and option checkboxes. Public constructors and helpers include `dialog_new()`, `dialog_create()`, `dialog_modal_loop()`, `dialog_input*()`, `dialog_notice()`, `dialog_edit_value()`, `dialog_select_type()`, and `dialog_search_input()`.

## Control Flow

Callers build a dialog by appending sections, then `dialog_create()` computes size, creates pad/window/panel, creates section subpads, and focuses the first focusable section. `dialog_modal_loop()` repeatedly shows the dialog, updates panels, reads input via `regedit_getch()`, and lets `dialog_handle_input()` route keys to the current section or dialog submit callback. High-level input dialogs validate numeric or string entries. Value-edit dialogs select an editor mode based on registry type or forced binary mode, prefill current data, validate/serialize input, and call `reg_val_set()`.

## State and Persistence Behavior

Dialog state is talloc-owned and destroyed with the dialog. Text-field state lives in ncurses `FIELD`/`FORM` objects; hex data lives in a `struct hexedit`. `dialog_edit_value()` can persistently create or update registry values. Search dialogs update the caller's `regedit_search_opts`, freeing and replacing the query string.

## Dependencies and Integration Points

The file integrates ncurses panels, menus, and forms; `regedit_getch()` for resize-aware input; `regedit_hexedit`; `regedit_valuelist` value items; registry serialization helpers such as `push_reg_sz`, `pull_reg_multi_sz`, and `regtype_by_string`; and Samba registry write API `reg_val_set()`.

## Risks and Edge Cases

Focus traversal loops until a section accepts focus, so dialogs with no focusable section would loop. `dialog_destroy()` assumes `head_section` is non-NULL. `text_field_on_input()` increments length for all default input, including control keys not specially handled. `dialog_input_internal()` sets `*req.out.out_str = NULL` even for numeric output via a union, which is harmless for pointer-sized storage only if callers pass valid output storage. Binary value editing can grow buffers interactively and must handle allocation failure.

## Test Signals

Tests should cover dialog resize, focus traversal, tab/backtab, numeric validation, cancel paths, duplicate or blank value names, REG_DWORD range validation, REG_SZ/EXPAND_SZ/MULTI_SZ serialization, forced binary editing, buffer resize, search option validation, and memory cleanup under valgrind or sanitizer-enabled curses tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/regedit_dialog.c -->
