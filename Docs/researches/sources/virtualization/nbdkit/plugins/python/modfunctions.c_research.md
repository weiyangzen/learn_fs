# File Research: sources/virtualization/nbdkit/plugins/python/modfunctions.c

## Purpose
Defines the built-in Python `nbdkit` module exposed to Python plugins, including utility functions and nbdkit constants.

## Main Entry Points
Exports Python-callable functions for debug logging, hexdump/hexdiff, export name, errno setting, shutdown, disconnect, size/probability/delay/bool parsing, stdio safety, TLS state, nanosleep, peer PID/UID/GID/security/TLS identity, password reading, process name, and timestamp. `create_nbdkit_module()` creates the module and adds thread-model, flag, FUA, cache, and extent constants.

## Internal Mechanics
`last_error` is thread-local and records errno set by `nbdkit.set_error()` for callback fallback handling elsewhere in the adapter. Buffer utilities use Python buffer protocol parsing and pass memory directly to nbdkit debug helpers.

## Dependencies
Uses Python C API, nbdkit plugin API/helper functions, and `plugin.h` declarations.

## Risks and Notes
`do_debug_hexdiff()` returns on unequal buffer lengths without releasing acquired `Py_buffer` objects, leaking buffer exports on that error path. `parse_size()` converts the parsed `int64_t` through `PyLong_FromSize_t`, which can be a portability issue if very large sizes exceed `size_t` on a target. `peer_name` is intentionally not implemented because CPython’s socket sockaddr conversion helper is not exported.
