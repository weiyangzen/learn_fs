# File Research: sources/virtualization/nbdkit/plugins/ocaml/buf.c

## Purpose
Provides optimized C stubs for copying between OCaml strings/bytes and nbdkit buffer bigarrays.

## Main Entry Points
- `ocaml_nbdkit_blit_from()` copies from an OCaml string into a bigarray-backed buffer.
- `ocaml_nbdkit_blit_to_bytes()` copies from a bigarray-backed buffer into OCaml bytes.

## Dependencies
Uses OCaml bigarray and value APIs plus nbdkit plugin visibility macros.

## Risks and Notes
These functions are marked noalloc-style and perform raw `memcpy` with caller-provided positions and lengths. Bounds validation is expected to happen on the OCaml side; the C stubs trust indices.
