# File Research: sources/virtualization/nbdkit/server/internal.h

Purpose: Central private server header tying together global configuration, connection/context state, backend vtables, server helpers, and cross-module declarations.

Global state:
- Declares command-line/server globals such as `foreground`, `read_only`, `tls`, `tls_psk`, `unixsocket`, `threads`, `timeout`, `verbose`, `service_mode`, `configured`, and `top`.
- Defines `enum log_to` and `enum service_mode`.
- Exposes `service_mode_string`.

Core constants/macros:
- `MAX_API_VERSION` and `NBDKIT_API_VERSION`.
- `MAX_REQUEST_SIZE` = 64 MiB.
- `DO_DLCLOSE` policy varies under ASan, fuzzing, and Valgrind.
- DTrace probe macros become no-ops when probes are disabled.
- `debug()` macro routes server debug through `debug_in_server`.
- `GET_CONN` pulls the current connection from thread-local storage and asserts non-null.

Connection/context model:
- `struct context` stores per-backend/per-connection handle state, export name, cached size/capabilities, next context, and lifecycle state bits.
- `struct connection` stores locks, status, TLS session, worker count, top context, default export names, protocol flags, interned strings, sockets, and transport function pointers.
- Connection transport is abstracted through recv/send/close function pointers, allowing TLS replacement.

Backend model:
- `struct backend` is the internal vtable implemented by plugins and filters.
- It includes lifecycle, configuration, export discovery, open/prepare/finalize/close, capability, and data-operation callbacks.
- Backend chain is linked by `next`; plugin is last with index 0, filters have higher indices.

Declared modules:
- Connection handling, protocol handshake/request processing, crypto, debug flags, logging, backend operations, plugin/filter registration, locks, sockets, thread-local state, exports, timeout, signals, backgrounding, user/group changes, URI generation, and socket activation.

Design role:
- This header defines the internal ABI between server modules, while public plugin/filter ABI comes from `nbdkit-plugin.h` and `nbdkit-filter.h`.
