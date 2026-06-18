# sources/user-network-fs/nfs-ganesha/src/scripts/ganeshactl/ganeshactl.py

## Purpose

`ganeshactl.py` is the graphical NFS-Ganesha administration tool. It wires the generated main window UI to PyQt DBus wrappers for admin, export, client, and log operations.

## Important APIs, Types, and Functions

`MainWindow(QtGui.QMainWindow)` defines `show_status` and methods for menu actions: `quit`, `connect_gsh`, `add_client`, `remove_client`, `export_mgr`, `logsettings`, `reset_grace`, `shutdown`, `reload`, `stats`, `view_exports`, `view_clients`, `help`, and `status_message`. The main block creates `QApplication`, gets the system bus, shows the window, and runs the event loop.

## Control Flow

Construction loads `Ui_MainWindow`, creates DBus wrappers, creates `LogSetDialog`, connects menu actions, creates export/client table models, and installs them on the table views. User actions either prompt for input, call DBus wrappers, show dialogs, or fetch current table data. DBus status replies update the status bar.

## State and Persistence Behavior

GUI state includes wrapper objects, table models, and the log dialog. Persistent effects are remote DBus operations: add/remove clients, grace, shutdown, reload, and log setting changes.

## Dependencies and Integration Points

It depends on PyQt5, generated UI modules, `Ganesha.admin`, `export_mgr`, `client_mgr`, `log_mgr`, and Qt table/dialog modules. It requires a system bus service `org.ganesha.nfsd`.

## Risks and Edge Cases

The code imports widgets from `QtGui`, but PyQt5 places many widgets in `QtWidgets`. It uses `quit()` rather than application quit. Several menu actions are placeholders. It does not validate IP addresses or protect reload/shutdown beyond a message box. Underlying table/log models contain additional Python 2/PyQt compatibility risks.

## Test Signals

GUI smoke tests should instantiate `MainWindow` with a fake DBus connection or fake wrappers, verify all action connections, and exercise table refreshes. Manual/integration tests should cover DBus error reporting and privileged operations.
