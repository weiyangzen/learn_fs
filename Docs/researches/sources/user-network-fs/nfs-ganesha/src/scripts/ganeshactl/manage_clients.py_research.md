# sources/user-network-fs/nfs-ganesha/src/scripts/ganeshactl/manage_clients.py

## Purpose

`manage_clients.py` is an older Qt event-loop CLI for adding, removing, and showing Ganesha clients.

## Important APIs, Types, and Functions

`ManageClients(QtCore.QObject)` owns a PyQt `ClientMgr`, emits/receives status, and provides `addclient`, `removeclient`, `showclients`, `proc_clients`, and `status_message`. The main block dispatches `add`, `remove`, and `show`.

## Control Flow

The script creates a `QApplication`, installs `DBusQtMainLoop`, opens the system bus, constructs the wrapper, calls the requested asynchronous DBus method, and enters the event loop. Completion callbacks print results and call `sys.exit`.

## State and Persistence Behavior

No local persistence exists. Add/remove mutate daemon client state; show is read-only.

## Dependencies and Integration Points

It depends on PyQt5, dbus Qt mainloop integration, and `Ganesha.client_mgr.ClientMgr`. It overlaps with `ganesha_mgr.py`.

## Risks and Edge Cases

It indexes argv without length checks. `QApplication` is imported from `PyQt5.QtGui`, which is usually wrong for PyQt5. Printed columns omit NFSv4.2 while the namedtuple includes it. Error and success statuses both go through `status_message` text beginning with `Error:`.

## Test Signals

CLI tests should cover missing/unknown commands, mocked add/remove/show completions, and PyQt5 import smoke. Integration tests can be limited because `ganesha_mgr.py` covers the newer path.
