# sources/user-network-fs/mergerfs/src/state.cpp

## Purpose
Defines the global `State state` object and implements dynamic get/set/validation hooks for runtime state exposed through xattrs or control interfaces.

## Important APIs, Types, and Functions
`State::State()` currently performs no registration. `set_getset()` installs a named `GetSet` handler. `get()`, `set()`, and `valid()` look up handlers and return `-ENOATTR` when the key or requested callback is unavailable.

## Control Flow
Lookup uses the `_getset` map. Successful get invokes the stored getter into an output string; set and valid call their stored callbacks with the provided string view.

## State and Persistence Behavior
The global `state` object persists for process lifetime. `_getset` stores callbacks, and `open_files` state is declared in the header. No on-disk persistence is performed.

## Dependencies and Integration Points
Depends on `state.hpp` and `errno.hpp`. It integrates with control xattr code that maps `user.mergerfs.*` keys to live configuration values.

## Risks and Edge Cases
The `_getset` map has no visible synchronization here; concurrent registration and access would need external ordering. Commented-out getattr registration indicates unfinished or removed runtime control surface.

## Test Signals
Test registered get/set/valid callbacks, missing keys returning `ENOATTR`, callback error propagation, and concurrent access expectations.
