# sources/security-integrity/selinux/gui/fcontextPage.py

## Purpose

`fcontextPage.py` implements the GTK page for viewing and editing SELinux file context mappings.

## Important APIs, Types, And Methods

The local `context` class splits a displayed context string into type and MLS components. `fcontextPage` extends `semanagePage` and uses `seobject.fcontextRecords()` for reads plus `semanage fcontext` commands for writes. Columns are file specification, SELinux file type/range, and file type option.

Key methods are `load(filter)`, `match(fcon_dict, k, filter)`, `dialogInit()`, `dialogClear()`, `add()`, `modify()`, and `delete()`.

## Control Flow

Initialization creates a three-column view, loads fcontext records, populates the file type combo from `seobject.file_type_str_to_option`, and stores dialog entries. `load()` reads all records, optionally sorting keys, filters by tuple and context values, formats type/range with `seobject.translate()`, and selects the first row. Dialog initialization locks the file spec and file type for existing entries and splits the selected context into type/range fields. Add/modify/delete construct `semanage fcontext` commands with `-a`, `-m`, or `-d`.

## State And Persistence

The UI store mirrors fcontext records. Persistent changes are made to local semanage fcontext configuration. MLS/range input defaults to `s0` for new entries.

## Dependencies And Integration Points

It depends on GTK, `seobject`, `semanagePage`, `semanage`, and UI IDs for `fcontextView`, filter entry, text entries, and combo box. It integrates with restorecon workflows indirectly because changed mappings need relabeling to affect files.

## Risks

The `match()` method reuses variable `k` inside loops and then indexes `fcon_dict[k]` after `k` may have become a string element rather than the original tuple, so filtering can silently fail under the broad `except`. Command strings quote file specs but not type or MLS values. Incorrect user input can be passed to semanage and reported through dialogs.

## Test Signals

Tests should cover loading and filtering of tuple keys, dialog setup for contexts with and without MLS parts, combo population, and exact semanage command construction for add/modify/delete. A focused test for `match()` would expose the variable shadowing behavior.
