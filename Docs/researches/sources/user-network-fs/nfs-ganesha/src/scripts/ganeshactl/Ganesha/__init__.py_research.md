# sources/user-network-fs/nfs-ganesha/src/scripts/ganeshactl/Ganesha/__init__.py

## Purpose

This package initializer defines the public `Ganesha` Python management package used by both GUI and command-line administration tools.

## Important APIs, Types, and Functions

The file exposes `admin`, `io_stats`, `export_mgr`, `client_mgr`, and `log_mgr` through `__all__`.

## Control Flow

Importing `Ganesha` performs no dynamic work beyond setting `__all__`; concrete behavior lives in the listed modules.

## State and Persistence Behavior

No runtime state or persistence is defined.

## Dependencies and Integration Points

`setup.py.in` packages `Ganesha`. GUI and wrapper scripts import modules from this package to reach PyQt DBus interfaces, table models, and stats types.

## Risks and Edge Cases

`__all__` does not list newer synchronous helper modules such as `ganesha_mgr_utils` and `glib_dbus_stats`, though they are still importable by full name. Listed `io_stats` is currently broken on import because its namedtuple field declarations are malformed and `Object` is undefined.

## Test Signals

Import smoke tests should cover `import Ganesha` and each named submodule to catch packaging and syntax/runtime import regressions.
