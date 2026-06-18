# File Research: sources/virtualization/nbdkit/plugins/python/examples/ramdisk.py

## Purpose
Example Python plugin implementing a 1 MiB in-memory ramdisk using a global `bytearray`.

## Main Entry Points
- `config()` logs and ignores extra parameters.
- `open()` logs readonly/TLS state and returns a simple handle.
- `get_size()` returns bytearray length.
- `pread()` copies from the bytearray into the supplied buffer.
- `pwrite()` writes from the buffer into the bytearray.
- `zero()` zeroes when `FLAG_MAY_TRIM` is set, otherwise sets EOPNOTSUPP and raises to trigger fallback.

## Dependencies
Uses `nbdkit`, `errno`, and API version 2 buffer semantics.

## Risks and Notes
The global bytearray is shared by all clients and no explicit thread model is declared. Python execution is GIL-constrained, but production plugins should still reason about concurrent logical updates.
