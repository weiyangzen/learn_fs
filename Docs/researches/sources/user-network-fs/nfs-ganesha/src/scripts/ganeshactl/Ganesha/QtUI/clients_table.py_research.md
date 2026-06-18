# sources/user-network-fs/nfs-ganesha/src/scripts/ganeshactl/Ganesha/QtUI/clients_table.py

## Purpose

`clients_table.py` implements the Qt table model used by the GUI Clients tab. It adapts `ClientMgr.ShowClients` DBus replies into displayable rows with protocol availability columns and last-stat-update time.

## Important APIs, Types, and Functions

`ClientTableModel(QAbstractTableModel)` exposes `FetchClients`, `FetchClients_done`, Qt model methods (`setData`, `insertRows`, `removeRows`, `rowCount`, `columnCount`, `headerData`, `flags`, `data`), and stores rows in `self.clients`. Headers cover client IP, NFSv3, MNT, NLMv4, RQUOTA, NFSv4.0, NFSv4.1, 9P, and last update.

## Control Flow

Construction stores the DBus manager, subscribes to `clientmgr.show_clients`, and initializes an empty row list. `FetchClients` calls `ClientMgr.ShowClients`; the asynchronous DBus wrapper later emits `show_clients`, invoking `FetchClients_done`. The handler resizes the table if the client count changed, then formats booleans as `yes`/`no`, timestamp tuples through `time.ctime`, and all other cells as strings before calling `setData`.

## State and Persistence Behavior

All state is in memory: `self.clients` holds the rendered cell strings and `self.ts` is initialized but not updated. The model does not persist client data and does not mutate server state.

## Dependencies and Integration Points

It depends on PyQt5 core/table model classes and `QColor`, and on a manager object compatible with `Ganesha.client_mgr.ClientMgr`. It is used by `ganeshactl.py` as the model for `ui.clients`.

## Risks and Edge Cases

The code uses Python 2/PyQt4 idioms (`xrange`, `self.emit(SIGNAL(...))`, `QVariant`) while the scripts are Python 3/PyQt5, so the model is likely to fail at runtime without compatibility shims. The alignment branch checks column `9`, but the header has 9 columns indexed `0..8`, so the last-update column is not aligned as intended. The namedtuple currently includes NFSv4.2 in the manager, while this UI header omits it, so protocol data can be shifted or truncated if row lengths differ from the model column count.

## Test Signals

Useful tests instantiate the model with a fake manager signal, emit client rows of varying lengths, verify row insertion/removal, and check display roles for booleans, timestamps, colors, and alignment. A PyQt5 import/runtime smoke test is important because this file mixes old and new Qt APIs.
