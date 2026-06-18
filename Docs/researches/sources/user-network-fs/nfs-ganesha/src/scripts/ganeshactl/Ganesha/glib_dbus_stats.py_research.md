# sources/user-network-fs/nfs-ganesha/src/scripts/ganeshactl/Ganesha/glib_dbus_stats.py

## Purpose

`glib_dbus_stats.py` is the statistics retrieval and formatting library for `ganesha_stats.py`. It calls Ganesha export/client stats DBus methods and exposes text and JSON report objects for global, export, client, protocol, pNFS, FSAL, authentication, and detailed operation counters.

## Important APIs, Types, and Functions

Top-level helpers are `dbus_to_std`, `timestr`, and `report_key_value`. `Report` is the base for JSON-producing report classes. Retrieval classes are `RetrieveExportStats` and `RetrieveClientStats`. Report/parsing classes include `ClientStats`, `ProtocolsStats`, `Client`, `DelegStats`, `ClientIOops`, `ClientAllops`, `Export`, `ExportStats`, `ExportDetails`, `GlobalStats`, `InodeStats`, `FastStats`, `ExportIOv3Stats`, `ExportIOv4Stats`, `ExportIOv41Stats`, `ExportIOv42Stats`, `ExportIOMonStats`, `TotalStats`, `PNFSStats`, `StatsReset`, `StatsStatus`, `DumpFSALStats`, `StatsEnable`, `StatsDisable`, `DumpAuth`, `DumpFULLV3Stats`, and `DumpFULLV4Stats`.

## Control Flow

Retrieval objects bind the system bus and object paths, obtain DBus methods, and return report objects. Report construction stores raw reply tuples and often extracts timestamps/status fields. `Report.report` builds a status header and delegates to `fill_report`; `json` serializes that structure. Text output is implemented through `__str__` on each report. Multi-export commands first list exports and call per-export stats methods, then aggregate results keyed by export ID.

## State and Persistence Behavior

State is in-memory raw DBus replies plus parsed fields. Reset/enable/disable commands mutate daemon statistics counters or collection state remotely. Other commands are read-only.

## Dependencies and Integration Points

It depends on Python `dbus`, `time`, `json`, and `sys`. `ganesha_stats.py` selects report methods from this module. It integrates with `org.ganesha.nfsd.exportstats`, `org.ganesha.nfsd.exportmgr`, `org.ganesha.nfsd.clientstats`, and `org.ganesha.nfsd.clientmgr`.

## Risks and Edge Cases

The module has a large positional parsing surface and uses assertions for type assumptions; optimized Python can skip assertions. `Report._header` has an inner function parameter that is unused and references outer `result`. Some report classes do not call `Report.__init__` and/or do not implement JSON, which is why `ganesha_stats.py` excludes some commands. There are duplicate/fragile counter walks and several unused locals. Backend schema changes or unavailable stats can cause `IndexError`, `StopIteration`, or failed type assertions.

## Test Signals

Unit tests should feed representative DBus-like tuples for every report class and validate both `str()` and `json()` where supported. Integration tests should cover `ganesha_stats` commands against a daemon with stats enabled/disabled, empty exports/clients, and per-export all-export aggregation. Negative tests should include DBus failures and malformed reply shapes.
