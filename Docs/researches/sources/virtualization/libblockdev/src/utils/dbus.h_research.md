# File Research: sources/virtualization/libblockdev/src/utils/dbus.h

This public header declares the D-Bus utility API.

Definitions:
- `BD_UTILS_DBUS_ERROR` maps to `bd_utils_dbus_error_quark()`.
- `BDUtilsDBusError` defines generic failure and no-exist variants.
- Declares `bd_utils_dbus_service_available()`.

Research relevance:
- The enum is broader than the current implementation, which mainly propagates GIO errors and returns `FALSE` for missing services without setting a custom no-exist error.
