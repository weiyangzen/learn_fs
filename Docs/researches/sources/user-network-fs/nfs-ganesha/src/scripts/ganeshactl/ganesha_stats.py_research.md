# sources/user-network-fs/nfs-ganesha/src/scripts/ganeshactl/ganesha_stats.py

## Purpose

`ganesha_stats.py` is the command-line frontend for reading and controlling Ganesha statistics counters over DBus, with optional JSON output for many report types.

## Important APIs, Types, and Functions

`print_usage_exit` renders usage. Top-level parsing handles commands including `global`, `list_clients`, `deleg`, `inode`, `iov3`, `iov4`, `iov41`, `iov42`, `iomon`, `export`, `total`, `fast`, `pnfs`, `fsal`, `reset`, `enable`, `disable`, `status`, `v3_full`, `v4_full`, `auth`, `client_io_ops`, `export_details`, and `client_all_ops`. It uses `RetrieveExportStats` and `RetrieveClientStats` from `Ganesha.glib_dbus_stats`.

## Control Flow

The default command is `global`. A leading `json` switches output mode and shifts the command. The script validates required IPs, export IDs, FSAL names, and stat-type arguments, then creates both export and client retrieval interfaces. It dispatches to the selected retrieval method and prints either `result.json()` or `str(result)`.

## State and Persistence Behavior

Most commands are read-only. `reset`, `enable`, and `disable` mutate server statistics counter state. There is no local persistence.

## Dependencies and Integration Points

It depends on `Ganesha.glib_dbus_stats` and `dbus`. It integrates with multiple Ganesha DBus stats interfaces through that library.

## Risks and Edge Cases

Both retrieval interfaces are constructed for every command, so client DBus availability can affect export-only commands and vice versa. JSON mode excludes `fsal`, `reset`, `enable`, and `disable`, but other classes may still have incomplete JSON behavior if library support drifts. Manual argument parsing uses `isdigit`, so negative export IDs are only represented by omission and non-decimal forms are rejected.

## Test Signals

CLI tests should cover default command, JSON command shifting, usage failures, stat-type validation, and each dispatch branch with mocked retrieval objects. Integration tests should run representative text and JSON commands against a daemon.
