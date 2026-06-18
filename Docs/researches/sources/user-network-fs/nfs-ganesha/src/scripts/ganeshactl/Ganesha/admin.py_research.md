# sources/user-network-fs/nfs-ganesha/src/scripts/ganeshactl/Ganesha/admin.py

## Purpose

`admin.py` implements the PyQt DBus client for the `org.ganesha.nfsd.admin` interface used by the GUI and older Qt command-line wrapper.

## Important APIs, Types, and Functions

`AdminInterface(QtDBus.QDBusAbstractInterface)` binds a service/path/connection to interface `org.ganesha.nfsd.admin`. It exposes `grace(ipaddr)`, `reload()`, `shutdown()`, and completion handler `admin_done(call)`.

## Control Flow

Each public method issues `asyncCall` to DBus and wraps the returned pending call in `QDBusPendingCallWatcher`. The watcher emits `finished`, invoking `admin_done`. The handler converts DBus errors into `show_status(False, ...)`; successful replies are expected as `(status, msg)` and are emitted through the supplied status signal.

## State and Persistence Behavior

The object keeps only the `show_status` signal reference and DBus interface metadata. Persistent effects are remote daemon actions: grace-period reset, config reload, or daemon shutdown.

## Dependencies and Integration Points

It depends on PyQt5 `QtDBus` and is used by `ganeshactl.py` and `ganesha-admin.py`. It expects the server to own `org.ganesha.nfsd` and expose `/org/ganesha/nfsd/admin`.

## Risks and Edge Cases

The reply conversion uses `argumentAt(...).toPyObject()`, which may not match modern PyQt5 DBus value APIs. There is no timeout, input validation, or argument-count validation. Shutdown and reload are privileged/high-impact operations gated only by the caller UI.

## Test Signals

Use a fake or test DBus service returning success/error tuples and assert emitted `show_status` values. GUI tests should verify grace/reload/shutdown action wiring and error reporting when Ganesha is down.
