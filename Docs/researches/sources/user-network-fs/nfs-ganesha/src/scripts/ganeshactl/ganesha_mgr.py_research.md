# sources/user-network-fs/nfs-ganesha/src/scripts/ganeshactl/ganesha_mgr.py

## Purpose

`ganesha_mgr.py` is the main synchronous command-line administration tool for NFS-Ganesha. It wraps client/export management, admin operations, cache views/purges, standard log levels, and conditional logging controls.

## Important APIs, Types, and Functions

Wrapper classes are `ManageClients`, `ShowExports`, `ServerAdmin`, `ManageCache`, `ManageLogs`, and `ManageCondLogs`. Helper exits are `exit_try_help` and `exit_option_not_supported`. The main block defines a large usage string and dispatches commands: `add`, `remove`, `update`, `display`, `purge`, `show`, `grace`, `trim`, `set`, `get`, `getall`, `shutdown`, and `help`.

## Control Flow

At startup, the script constructs all manager wrappers, which open DBus connections. It then parses positional arguments and calls the selected wrapper method. Output is printed directly. Conditional logging commands route to `CondLogManager`; standard log commands route to `LogManager`; admin commands route to `AdminInterface`.

## State and Persistence Behavior

Local state is transient wrapper instances. Remote persistent/runtime effects include adding/removing clients and exports, changing log levels and conditional logging policy/targets, purging caches, toggling malloc trim, grace-period operations, and shutdown.

## Dependencies and Integration Points

It depends on `Ganesha.ganesha_mgr_utils`, Python `os`, `sys`, and `time`, and a live Ganesha DBus service. It supersedes several older single-purpose Qt command-line scripts.

## Risks and Edge Cases

Because all wrappers are constructed before command validation, even `help` requires a working DBus service. Argument parsing is manual and inconsistent. Destructive commands such as shutdown and export removal have no confirmation. A special guard detects likely shell expansion of `*` for conditional client removal, which is useful but narrow. Some print methods omit NFSv4.2 despite data classes containing it.

## Test Signals

CLI tests should cover every command branch, missing arguments, unknown options, conditional `*` guard behavior, and DBus down behavior. Mock utility managers allow command dispatch testing without a daemon; integration tests should cover real DBus calls in a controlled environment.
