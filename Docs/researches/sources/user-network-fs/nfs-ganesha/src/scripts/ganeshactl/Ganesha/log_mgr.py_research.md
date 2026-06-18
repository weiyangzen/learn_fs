# sources/user-network-fs/nfs-ganesha/src/scripts/ganeshactl/Ganesha/log_mgr.py

## Purpose

`log_mgr.py` implements the PyQt DBus wrapper for querying and changing Ganesha log component levels through the standard `org.freedesktop.DBus.Properties` interface.

## Important APIs, Types, and Functions

Constants are `ADMIN_OBJECT`, `PROP_INTERFACE`, and `LOGGER_PROPS`. `LogManager(QDBusAbstractInterface)` emits `show_components` and `show_level`; methods are `GetAll`, `GetAll_done`, `Get`, `Get_done`, `Set`, and `Set_done`.

## Control Flow

The wrapper binds to `/org/ganesha/nfsd/admin` using `org.freedesktop.DBus.Properties`. `GetAll` calls `GetAll(LOGGER_PROPS)`, unwraps a DBus map of component names to levels, and emits a Python dict. `Get` emits one level string. `Set` wraps the level in `QDBusVariant` and calls `Set(LOGGER_PROPS, prop, value)`, then emits status.

## State and Persistence Behavior

The object stores only DBus metadata and a status signal. `Set` mutates live server log level properties; no local persistence is maintained.

## Dependencies and Integration Points

It depends on PyQt5 `QtCore` and `QtDBus`. It is used by `LogSettingsModel`, `manage_logger.py`, and `ganeshactl.py`.

## Risks and Edge Cases

Like other Qt DBus wrappers, it uses older `toPyObject`/`toString` conversion patterns. `Set` passes plain strings through `QDBusVariant.setVariant`, which may not create the exact DBus variant type expected by all PyQt5 versions. Property names are not normalized with `COMPONENT_` here, unlike the synchronous helper.

## Test Signals

DBus fixture tests should validate `GetAll` map conversion, `Get` single-level conversion, successful `Set`, and error propagation. GUI tests should verify that editing the log-level table results in the expected DBus property call.
