# sources/user-network-fs/nfs-ganesha/src/scripts/ganeshactl/Ganesha/export_mgr.py

## Purpose

`export_mgr.py` provides PyQt DBus wrappers for export management and export statistics interfaces.

## Important APIs, Types, and Functions

`Export` is a namedtuple containing export ID/path, protocol availability flags, and last time. `ExportMgr(QDBusAbstractInterface)` exposes `AddExport`, `UpdateExport`, `RemoveExport`, `DisplayExport`, `ShowExports`, and completion handlers. It emits `show_exports` and `display_export`. `ExportStats` wraps `GetNFSv3IO`, `GetNFSv40IO`, `GetNFSv41IO`, and `GetNFSv41Layouts`, with stub handlers.

## Control Flow

Export operations use asynchronous Qt DBus calls. Add/update expect a returned message, remove expects success without payload, display emits ID/full path/pseudo/tag, and show parses a timestamp plus an export array into namedtuples before emitting `show_exports`.

## State and Persistence Behavior

The wrapper stores only interface metadata and status signal references. Add/update/remove mutate the daemon's live export configuration. Show/display are read-only.

## Dependencies and Integration Points

It depends on PyQt5 and feeds `ExportTableModel`, `manage_exports.py`, and `ganeshactl.py`. It expects DBus service `org.ganesha.nfsd`, path `/org/ganesha/nfsd/ExportMgr`, and interfaces `org.ganesha.nfsd.exportmgr`/`exportstats`.

## Risks and Edge Cases

Reply parsing is positional and tied to older Qt variant methods. The namedtuple has NFSv4.2, but table and older print code omit it. `DisplayExport` ignores client detail data in this Qt wrapper, unlike the synchronous helper. Stats callbacks are unimplemented. Export IDs are converted to `int` without range checks.

## Test Signals

Tests should simulate DBus replies for add/update/remove/display/show, including empty export lists and NFSv4.2 data. End-to-end tests with a running test Ganesha DBus service should verify live export changes and UI table updates.
