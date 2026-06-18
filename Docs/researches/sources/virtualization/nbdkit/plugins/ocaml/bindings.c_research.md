# File Research: sources/virtualization/nbdkit/plugins/ocaml/bindings.c

## Purpose
Provides OCaml C stubs for miscellaneous `nbdkit_*` utility APIs exposed by the OCaml plugin support library.

## Main Entry Points
Exports OCaml-callable wrappers for error setting, size/probability/bool/delay parsing, password reading, stdio safety, realpath, nanosleep, export name, TLS state, shutdown, disconnect, debug logging, hexdump/hexdiff, timestamp, version/API version, process name, peer socket identity, peer PID/UID/GID, security context, and TLS distinguished names.

## Internal Mechanics
Wrappers convert OCaml strings, ints, int64s, options, tuples, bigarrays, and Unix error values into nbdkit C API calls. Blocking operations such as `nbdkit_nanosleep` release the OCaml runtime while sleeping. Optional socket-address support is compiled only when `HAVE_CAML_SOCKETADDR_H` is present.

## Dependencies
Uses OCaml runtime headers, bigarray support, Unix error conversion, nbdkit plugin API v2, and `plugin.h` compatibility/runtime-lock helpers.

## Risks and Notes
Most parse wrappers raise `Invalid_argument` or `Failure` on nbdkit errors and do not preserve detailed errno beyond the OCaml exception. `ocaml_nbdkit_debug_hexdiff()` validates equal bigarray byte sizes before calling nbdkit. `peer_name` support depends on OCaml runtime headers; unsupported builds expose a stub that always fails.
