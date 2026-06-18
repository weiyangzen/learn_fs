# sources/user-network-fs/nfs-ganesha/src/scripts/ganeshactl/ganesha-admin.py

## Purpose

`ganesha-admin.py` is an older Qt event-loop command-line wrapper for Ganesha admin DBus operations: shutdown, reload, and grace.

## Important APIs, Types, and Functions

`ServerAdmin(QtCore.QObject)` owns an `AdminInterface`, exposes `shutdown`, `reload`, `grace`, and prints results in `status_message`. The main block creates a `QApplication`, installs `DBusQtMainLoop`, opens the system bus, dispatches based on `sys.argv[1]`, and runs the Qt event loop.

## Control Flow

Each command invokes an asynchronous `AdminInterface` method and prints an immediate action message. When the DBus reply arrives, `status_message` prints status/error text and exits the process.

## State and Persistence Behavior

No local persistence exists. Commands mutate remote daemon state through shutdown, reload, or grace-period calls.

## Dependencies and Integration Points

It depends on PyQt5, dbus-python's Qt mainloop integration, and `Ganesha.admin.AdminInterface`.

## Risks and Edge Cases

The script indexes `sys.argv[1]` and `sys.argv[2]` without length checks. It imports `QApplication` from `PyQt5.QtGui`, whereas PyQt5 normally provides it in `QtWidgets`. It has largely overlapping functionality with newer `ganesha_mgr.py`.

## Test Signals

CLI tests should cover missing/unknown commands and grace without IP. DBus mock tests should assert event-loop exit on successful and failed admin replies.
