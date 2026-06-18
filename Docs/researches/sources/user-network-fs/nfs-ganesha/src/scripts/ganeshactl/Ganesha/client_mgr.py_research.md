# sources/user-network-fs/nfs-ganesha/src/scripts/ganeshactl/Ganesha/client_mgr.py

## Purpose

`client_mgr.py` provides PyQt DBus wrappers for NFS-Ganesha client management and client statistics interfaces.

## Important APIs, Types, and Functions

`Client` is a namedtuple for client IP, protocol availability flags, and last activity time. `ClientMgr(QDBusAbstractInterface)` emits `show_clients` and provides `AddClient`, `RemoveClient`, `ShowClients`, `clientmgr_done`, and `clientshow_done`. `ClientStats` wraps `org.ganesha.nfsd.clientstats` methods `GetNFSv3IO`, `GetNFSv40IO`, `GetNFSv41IO`, and `GetNFSv41Layouts`, though completion handlers are stubs.

## Control Flow

Add/remove/show requests are issued asynchronously over Qt DBus. Add/remove completions emit a status message. `clientshow_done` parses the returned timestamp and client array, converts Qt DBus variants into Python strings, booleans, and timestamp tuples, builds `Client` rows, and emits `show_clients(ts, clients)`.

## State and Persistence Behavior

The wrapper stores only DBus metadata and status signal. Add/remove calls mutate the daemon's runtime client allow/deny state through DBus; show calls are read-only.

## Dependencies and Integration Points

It depends on PyQt5 `QtCore` and `QtDBus`. It feeds `ClientTableModel`, `manage_clients.py`, and `ganeshactl.py`.

## Risks and Edge Cases

Parsing relies on positional DBus reply layouts and PyQt variant conversion methods such as `toULongLong`, `toString`, and `toPyObject`. `Client` includes `HasNFSv42`, while old table/printing code often omits that column. Statistics methods are incomplete because their callbacks are `pass`. There is no validation for IP address inputs or DBus reply arity.

## Test Signals

DBus fixture tests should cover add/remove errors, empty and populated `ShowClients`, NFSv4.2 presence, and malformed replies. Import/runtime tests under PyQt5 should verify conversion APIs still exist.
