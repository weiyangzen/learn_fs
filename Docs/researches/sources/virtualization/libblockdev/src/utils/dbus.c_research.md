# File Research: sources/virtualization/libblockdev/src/utils/dbus.c

This file implements a D-Bus service availability helper using GIO.

Public functions:
- `bd_utils_dbus_error_quark()` returns the utility D-Bus error domain.
- `bd_utils_dbus_service_available()` checks whether a service is currently listed, activatable, and introspectable.

Availability flow:
- Uses an existing `GDBusConnection` if supplied, otherwise connects to the requested bus type.
- Calls `org.freedesktop.DBus.ListNames`.
- Calls `org.freedesktop.DBus.ListActivatableNames`.
- Searches both lists for `bus_name`.
- If found, calls `org.freedesktop.DBus.Introspectable.Introspect` on `obj_prefix` to verify access and possibly trigger activation.
- Returns `TRUE` only if the service is found and introspection succeeds.

Research relevance:
- This helper distinguishes “known/activatable name” from “usable service root”.
- Error details are mostly propagated from GIO calls; the local enum is defined but not used for custom errors in this implementation.
