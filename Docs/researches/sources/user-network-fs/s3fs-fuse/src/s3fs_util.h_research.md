# sources/user-network-fs/s3fs-fuse/src/s3fs_util.h

Purpose: declares the utility functions implemented by `s3fs_util.cpp` and defines a small RAII `scope_guard` helper for cleanup callbacks.

Important APIs and types: function declarations cover real path construction, sysconf initialization, user/group lookup, basename/dirname wrappers, directory creation/discovery/permission/deletion, launch logging, sensitive masking, and `s3fs_fclose`. `scope_guard` stores a `std::function<void()>`, calls it on destruction, and can be dismissed.

Control flow: call sites construct `scope_guard` around resources that need cleanup unless the operation is dismissed. Utility functions are used by startup, cache handling, request construction, and logging.

State and persistence: no state is declared in the header, but the implementation uses process globals and filesystem state.

Dependencies and integration points: includes `<functional>` and `<string>`, supplies clock fallback macros for portability, and is included by request, XML, and support modules.

Risks: `scope_guard` uses `std::function` and compares it to `nullptr`; this is convenient but heavier than a templated guard and only supports non-movable usage. Header-level clock macro fallbacks may mask platform differences.

Test signals: compile coverage for C++ standard versions supported by the project, RAII cleanup/dismiss behavior, and include-order portability tests around clock macros.
