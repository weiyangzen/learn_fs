# sources/user-network-fs/nfs-ganesha/src/scripts/ganeshactl/manage_exports.py

## Purpose

`manage_exports.py` is an older Qt event-loop CLI for showing, adding, updating, removing, and displaying Ganesha exports.

## Important APIs, Types, and Functions

`ShowExports(QtCore.QObject)` wraps `ExportMgr` and provides `showexports`, `addexport`, `updateexport`, `removeexport`, `displayexport`, `proc_export`, `proc_exports`, and `status_message`. The main block dispatches commands by argv.

## Control Flow

Like other Qt wrappers, it issues an asynchronous DBus call, enters the Qt event loop, and exits from completion callbacks after printing output. Display and show connect to dedicated export signals; add/update/remove use status callbacks.

## State and Persistence Behavior

No local persistence exists. Add/update/remove mutate live daemon export state; display/show are read-only.

## Dependencies and Integration Points

It depends on PyQt5, dbus Qt mainloop integration, and `Ganesha.export_mgr.ExportMgr`. It is superseded by `ganesha_mgr.py` for broader management.

## Risks and Edge Cases

Arguments are not length-checked before indexing. `QApplication` import location is likely incompatible with PyQt5. Print formatting omits NFSv4.2 even though the export tuple contains it. Export changes are not confirmed.

## Test Signals

Mocked DBus/PyQt tests should exercise every command and callback, including empty export lists and DBus errors. CLI tests should cover malformed invocation.
