# sources/user-network-fs/nfs-ganesha/src/scripts/ganeshactl/Ganesha/QtUI/ui_log_dialog.ui

## Purpose

This Qt Designer file defines the Log Settings dialog consumed by `log_settings.py`. It provides the visual container for editing component log levels.

## Important APIs, Types, and Functions

The UI class is `LogSettings`. It contains a `QTableView` named `log_levels` and a `QPushButton` named `log_done`. These object names are the integration API used by generated Python code and `LogSetDialog`.

## Control Flow

At build time, the `.ui` is converted into a Python `Ui_LogSettings` class. At runtime, `LogSetDialog.setupUi` creates the table and button; application code installs the table model/delegate and connects `log_done.clicked` to hide the dialog.

## State and Persistence Behavior

The file describes widget geometry and static text only. It has no data persistence. Server-side log state is handled by `LogSettingsModel`.

## Dependencies and Integration Points

It depends on Qt 4/5 UI compiler compatibility. It is referenced by the generated `Ganesha.QtUI.ui_log_dialog` module and `Ganesha.QtUI.log_settings`.

## Risks and Edge Cases

The layout uses fixed geometry for the button and an intermediate `verticalLayoutWidget`; resizing behavior may be weaker than a fully layout-managed dialog. If the generated Python class name or object names change, `LogSetDialog` will break.

## Test Signals

Build tests should confirm UI code generation. GUI smoke tests should instantiate `Ui_LogSettings`, find `log_levels` and `log_done`, and resize the dialog to verify usable layout.
