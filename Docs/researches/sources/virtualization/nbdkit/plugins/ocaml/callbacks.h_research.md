# File Research: sources/virtualization/nbdkit/plugins/ocaml/callbacks.h

## Purpose
Lists every nbdkit callback name supported by the OCaml plugin bridge through repeated `CB(name)` macro expansion.

## Main Contents
Includes lifecycle, configuration, export, capability, I/O, extent, cache, and threading callbacks: `load`, `config`, `open`, `pread`, `pwrite`, `zero`, `flush`, `trim`, `extents`, `thread_model`, `unload`, and others.

## Dependencies
This is intentionally not a normal guarded header; it is included multiple times by `plugin.c` with different `CB` definitions.

## Risks and Notes
Adding or removing a callback affects global root declarations, wrapper assignment, and root cleanup in `plugin.c`. The macro list is the central callback contract for OCaml plugins.
