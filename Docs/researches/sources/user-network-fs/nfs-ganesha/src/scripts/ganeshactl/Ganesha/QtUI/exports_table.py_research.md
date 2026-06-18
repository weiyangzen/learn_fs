# sources/user-network-fs/nfs-ganesha/src/scripts/ganeshactl/Ganesha/QtUI/exports_table.py

## Purpose

`exports_table.py` implements the Qt table model used by the GUI Exports tab. It transforms export-manager DBus data into a read-only table of export IDs, paths, protocol availability flags, and last statistics update time.

## Important APIs, Types, and Functions

`ExportTableModel(QAbstractTableModel)` owns `self.exports` and implements `FetchExports`, `FetchExports_done`, `setData`, row insertion/removal, `rowCount`, `columnCount`, `headerData`, `flags`, and `data`. Header columns are export ID, export path, NFSv3, MNT, NLMv4, RQUOTA, NFSv4.0, NFSv4.1, 9P, and last update.

## Control Flow

Construction subscribes to `exportmgr.show_exports`. `FetchExports` calls `ShowExports`; when the asynchronous wrapper emits results, `FetchExports_done` adjusts the row count, formats boolean and timestamp cells, and updates cell data. `data` services Qt display, alignment, background, and foreground roles.

## State and Persistence Behavior

The model stores only rendered table rows in memory. It has no persistence and does not perform server-side changes.

## Dependencies and Integration Points

It depends on PyQt5 and on `Ganesha.export_mgr.ExportMgr`. `ganeshactl.py` sets an instance as the model for the generated `exports` `QTableView`.

## Risks and Edge Cases

The source uses `xrange`, `QVariant`, and old signal emission patterns under a Python 3/PyQt5 shebang ecosystem. The manager's `Export` tuple includes NFSv4.2, but the table header does not; if all tuple elements are iterated, the model may address a column beyond `columnCount`. `setData` indexes `self.exports[row]` before checking bounds, so malformed indexes can raise before returning `False`.

## Test Signals

Fake-manager tests should emit empty, single-row, and resized export lists; assert row-count changes; and validate formatting of ID/path/protocol/time columns. GUI smoke tests should run under the exact PyQt5 version used by packages.
