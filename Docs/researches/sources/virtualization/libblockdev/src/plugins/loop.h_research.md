# File Research: sources/virtualization/libblockdev/src/plugins/loop.h

## Purpose

`loop.h` declares the public libblockdev loop plugin API and data structures.

## Public Types

- `BDLoopError` defines loop plugin error codes:
  - `BD_LOOP_ERROR_TECH_UNAVAIL`
  - `BD_LOOP_ERROR_FAIL`
  - `BD_LOOP_ERROR_DEVICE`
- `BDLoopTech` currently exposes one technology category, `BD_LOOP_TECH_LOOP`.
- `BDLoopTechMode` defines mode bits for create, destroy, modify, and query operations.
- `BDLoopInfo` describes a loop device:
  - backing file path
  - byte offset into backing file
  - autoclear flag
  - direct I/O flag
  - partition scan flag
  - read-only flag

## Public API

The header exposes:

- object lifetime helpers: `bd_loop_info_free()`, `bd_loop_info_copy()`
- plugin lifecycle: `bd_loop_init()`, `bd_loop_close()`
- availability probing: `bd_loop_is_tech_avail()`
- query helpers: `bd_loop_info()`, `bd_loop_get_loop_name()`
- creation helpers: `bd_loop_setup()`, `bd_loop_setup_from_fd()`
- destruction and modification helpers: `bd_loop_teardown()`, `bd_loop_set_autoclear()`, `bd_loop_set_capacity()`

## Integration Notes

The API is GLib-oriented: strings use `gchar`, booleans use `gboolean`, errors use `GError`, and returned objects/strings are caller-owned unless documented otherwise. It is intended to work both as a loaded libblockdev plugin and as a standalone library, with explicit init/close entry points.
