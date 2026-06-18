# sources/user-network-fs/nfs-ganesha/src/scripts/ganeshactl/Ganesha/QtUI/__init__.py

## Purpose

This package initializer declares the Qt UI submodules exported by `Ganesha.QtUI`. It is part of the Python package installed for the `ganeshactl` graphical administration tools and makes the generated UI modules and table/dialog model modules discoverable through package imports.

## Important APIs, Types, and Functions

The only runtime API is `__all__`, listing `exports_table`, `clients_table`, `ui_log_dialog`, `log_settings`, and `ui_main_window`.

## Control Flow

Importing the package executes no logic beyond binding `__all__`. Consumers import concrete modules directly, such as `Ganesha.QtUI.exports_table.ExportTableModel` or generated `Ui_MainWindow`.

## State and Persistence Behavior

There is no mutable state and no persistence. Package state is limited to module metadata.

## Dependencies and Integration Points

The file integrates with `setup.py.in`, which packages `Ganesha.QtUI`, and with `ganeshactl.py`, which imports generated Qt UI classes and table models from this package.

## Risks and Edge Cases

`__all__` includes generated modules (`ui_log_dialog`, `ui_main_window`) that must be produced during the build from `.ui` files. Missing generated Python UI files will break imports even though this initializer itself succeeds.

## Test Signals

Import smoke tests for `Ganesha.QtUI` and each listed submodule validate package installation and UI generation.
