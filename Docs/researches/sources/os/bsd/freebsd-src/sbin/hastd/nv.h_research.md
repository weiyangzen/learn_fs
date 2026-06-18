# File Research: sources/os/bsd/freebsd-src/sbin/hastd/nv.h

Read completely: 132 lines.

This header declares the HAST name/value API.

Key responsibilities:
- Declares allocation, freeing, error inspection, error setting, and validation.
- Declares conversion to/from `struct ebuf` network representation.
- Declares typed add/get functions for integer scalars, integer arrays, and strings.
- Declares formatted string helpers, existence/assertion helpers, and dump support.
- Annotates formatted-name APIs with `__printflike`.

Important interactions:
- Used across HAST daemon protocol, metadata, control, and event code.
- Exposes opaque `struct nv`, keeping wire details private to `nv.c`.

Reliability notes:
- The get functions return zero/NULL both for absent fields and true zero values; callers must use `nv_error()`, `nv_exists()`, or `nv_assert()` when absence matters.
