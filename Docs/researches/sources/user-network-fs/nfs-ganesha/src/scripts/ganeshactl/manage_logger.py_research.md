# sources/user-network-fs/nfs-ganesha/src/scripts/ganeshactl/manage_logger.py

## Purpose

`manage_logger.py` is an older Qt event-loop CLI for getting, setting, and listing Ganesha log component levels.

## Important APIs, Types, and Functions

`ManageLogger(QtCore.QObject)` wraps `LogManager` and provides `get_level`, `set_level`, `getall`, `proc_level`, `proc_components`, and `status_message`. The main block dispatches `get`, `set`, and `getall`.

## Control Flow

The script creates Qt/DBus event-loop state, issues one asynchronous log DBus request, enters the event loop, and exits from the callback after printing the level, component dictionary, or error.

## State and Persistence Behavior

No local persistence exists. `set` mutates live daemon log-level properties; `get`/`getall` are read-only.

## Dependencies and Integration Points

It depends on PyQt5, `DBusQtMainLoop`, and `Ganesha.log_mgr.LogManager`. It overlaps with `ganesha_mgr.py get/set/getall log`.

## Risks and Edge Cases

It indexes argv without validating argument count. `QApplication` import location is likely wrong for PyQt5. It uses the older Qt DBus wrapper, so conversion/API compatibility issues in `log_mgr.py` apply.

## Test Signals

Mocked tests should cover get/set/getall callbacks and error propagation. CLI tests should cover missing args and unknown command handling.
