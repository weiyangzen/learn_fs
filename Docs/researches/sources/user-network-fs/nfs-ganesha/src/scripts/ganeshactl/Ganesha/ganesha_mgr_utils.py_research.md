# sources/user-network-fs/nfs-ganesha/src/scripts/ganeshactl/Ganesha/ganesha_mgr_utils.py

## Purpose

`ganesha_mgr_utils.py` is the synchronous DBus utility layer behind the newer `ganesha_mgr.py` command-line tool. It wraps client, export, admin, cache, standard log, and conditional log DBus operations and normalizes results into status/message tuples and namedtuples.

## Important APIs, Types, and Functions

Namedtuples include `Client`, `Export`, `ExportClient`, `IDMapper`, `IDMapperGroup`, and `FileSys`. Classes are `ClientMgr`, `ExportMgr`, `AdminInterface`, `CacheMgr`, `LogManager`, and `CondLogManager`. `_log_component_prop_name` normalizes component names to `COMPONENT_*`.

## Control Flow

Each manager opens `dbus.SystemBus()`, obtains a daemon object, and stores the service/path/interface. Methods call `get_dbus_method`, catch `dbus.exceptions.DBusException`, and return `(False, ex, ...)` on failure. Show/list methods parse DBus arrays into namedtuples. Client/export protocol statistics are converted by JSON round-tripping DBus containers into Python data, then converting nested protocol pairs into dictionaries. Conditional log methods use the `org.ganesha.nfsd.log.conditional` interface for lists, match policy, and client/export enable/disable operations.

## State and Persistence Behavior

Manager instances keep DBus connection/object references. Persistent effects are remote daemon state changes: clients, exports, cache purges, malloc trim settings, log levels, conditional logging targets, and match policy. There is no local persistence.

## Dependencies and Integration Points

The module depends on `dbus`, `json`, `sys`, and `collections.namedtuple`. It is imported by `ganesha_mgr.py` and complements older PyQt wrappers. It uses Ganesha DBus paths `/org/ganesha/nfsd/ClientMgr`, `/ExportMgr`, `/admin`, and `/CacheMgr`.

## Risks and Edge Cases

Constructors catch all exceptions and call `sys.exit`, which prevents library-style error handling. JSON round-tripping assumes DBus values are serializable and can obscure type/range details. Many methods assume exact reply layouts. Conditional log list replies are interpreted as variable-length arrays ending in status and message; backend contract drift can misparse. Export IDs for conditional logging are cast to `dbus.UInt16`, so large IDs may fail or wrap depending on dbus behavior.

## Test Signals

Mock DBus object tests should cover success and `DBusException` for every manager method, protocol dictionaries with missing keys, conditional empty/non-empty lists, log component prefixing, and export ID conversion. Integration tests require a running Ganesha service exposing the expected DBus interfaces.
