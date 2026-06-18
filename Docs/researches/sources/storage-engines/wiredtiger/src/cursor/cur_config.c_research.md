# sources/storage-engines/wiredtiger/src/cursor/cur_config.c

## Purpose
This small file implements the `config:` cursor wrapper. It allocates a cursor with string key/value formats and delegates ordinary key/value accessor methods while making traversal and mutation unsupported.

## Important APIs, Types, and Functions
The public entry point is `__wt_curconfig_open`. The close method is `__curconfig_close`. The cursor type is `WT_CURSOR_CONFIG`, initialized with `WT_CURSOR_STATIC_INIT`.

## Control Flow and Behavior
Open allocates a `WT_CURSOR_CONFIG`, installs a static method table, sets the session and `S` key/value formats, and calls `__wt_cursor_init`. The method table supports get/set key/value and raw key/value helpers, no-op reset, checkpoint ID, and close; next, prev, search, insert, update, remove, reserve, reconfigure, bound, cache, and reopen are unsupported. Close runs through the cursor API macro and calls `__wt_cursor_close`.

## State and Persistence
The cursor owns only normal cursor lifetime state. It does not persist anything by itself; it exposes configuration data through cursor infrastructure determined elsewhere.

## Dependencies and Integration Points
The file depends on cursor initialization/close helpers, standard unsupported/no-op cursor methods, and the opaque pointer verification for `WT_CURSOR_CONFIG`. It integrates with `WT_SESSION->open_cursor` dispatch for config cursor URIs.

## Risks
Risks are low. The main issues would be method table drift if config cursors later need traversal, incorrect key/value formats, or failing to close partially initialized cursors on open error.

## Test Signals
Signals include opening and closing config cursors, correct string key/value format exposure, unsupported-operation errors for traversal/mutation, no-op reset behavior, and leak checks for failed opens.
