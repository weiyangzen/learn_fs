# sources/sync-backup/casync/src/udev-util.h

Purpose: provides a tiny cleanup integration point for libudev objects.

Important APIs/types/functions: defines cleanup functions/macros for `struct udev` or related udev references when udev support is compiled in.

Control flow/state: no runtime logic beyond cleanup wrappers; ownership follows libudev reference counting.

Dependencies/integration: used by device/NBD-related code that queries udev and wants `_cleanup_` style automatic unref.

Risks/test signals: header-only cleanup helpers are low risk, but conditional availability must match Meson feature detection. Device integration tests such as NBD paths are the likely signal.

Source research group: `subset-b-009122`.
