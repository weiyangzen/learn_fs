# File Research: sources/os/linux/linux-stable/fs/overlayfs/params.h

## Purpose

`params.h` declares overlayfs fs-context parsing structures and mount-parameter APIs shared between `params.c` and `super.c`.

## Main Definitions

- `ovl_parameter_spec[]`: parameter spec table consumed by VFS fs-parser.
- `ovl_parameter_redirect_dir[]`: redirect mode constant table exposed for parsing.
- `struct ovl_opt_set`: tracks whether selected options were explicitly set by the user, allowing `params.c` to distinguish automatic fallback from explicit conflicts.
- `OVL_MAX_STACK`: maximum total lower layer count, set to 500.
- `struct ovl_fs_context_layer`: stores a parsed layer name and resolved `struct path`.
- `struct ovl_fs_context`: stores parsed upper/work paths, lower layer array/capacity/counts, explicit option set, raw legacy lowerdir string, and casefold initialization state.

## Declared Functions

- `ovl_init_fs_context()`
- `ovl_free_fs()`
- `ovl_fs_params_verify()`
- `ovl_show_options()`
- `ovl_xino_mode()`

## Integration Notes

`super.c` consumes `struct ovl_fs_context` to allocate layers, clone mounts, build root lower stacks, and set up work/index dirs. `params.c` owns allocation, parsing, verification, and cleanup of this context.

## Risk Notes

The `nr` and `nr_data` fields are central to regular lower vs data-only lower semantics. Any user must preserve the invariant that data-only layers are counted in `nr` and also in the suffix count `nr_data`.
