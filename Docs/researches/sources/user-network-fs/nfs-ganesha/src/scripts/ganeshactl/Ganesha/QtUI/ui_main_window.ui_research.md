# sources/user-network-fs/nfs-ganesha/src/scripts/ganeshactl/Ganesha/QtUI/ui_main_window.ui

## Purpose

This Qt Designer file defines the main NFS-Ganesha GUI window used by `ganeshactl.py`. It provides tabs for exports and clients plus menu actions for DBus connection, administration, logging, views, and help.

## Important APIs, Types, and Functions

The generated class is `Ui_MainWindow`. Important named widgets/actions are `exports`, `clients`, `tabWidget`, `actionDBus_connect`, `actionQuit`, `actionAdd_Client`, `actionRemove_Client`, `actionExports`, `actionLog_Settings`, `actionReset_Grace`, `actionShutdown`, `actionReload`, `actionStatistics`, `actionViewExports`, `actionViewClients`, and `actionAbout`.

## Control Flow

At build time the UI is compiled to Python. At runtime `MainWindow.setupUi` creates the central tab widget, table views, menus, actions, and status bar. `ganeshactl.py` connects action signals to DBus wrapper methods and installs `ExportTableModel` and `ClientTableModel` on the table views.

## State and Persistence Behavior

The UI file contains only static widget configuration. Runtime state lives in table models and DBus wrappers. No persistence is represented here.

## Dependencies and Integration Points

It depends on Qt UI tooling and generated Python packaging. It is tightly coupled to object names expected by `ganeshactl.py`.

## Risks and Edge Cases

The UI still contains some actions that are placeholders or unused, such as `actionLog_Levels`. The scroll-area nesting around table views is more complex than necessary and can affect resizing. Menu/action naming is part of the code contract, so designer edits require matching Python changes.

## Test Signals

Tests should instantiate the generated UI, verify all action/widget names used by `ganeshactl.py` exist, and smoke-test table model installation and resize behavior.
