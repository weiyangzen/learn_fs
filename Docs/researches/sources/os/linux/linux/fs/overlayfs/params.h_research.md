# File Research: sources/os/linux/linux/fs/overlayfs/params.h

## Purpose

`params.h` declares the overlayfs fs-context and mount-parameter interface shared between `params.c` and `super.c`.

## Main Contents

- Includes fs-context and fs-parser declarations.
- Forward declares `struct ovl_fs` and `struct ovl_config`.
- Exposes `ovl_parameter_spec[]` for filesystem type registration.
- Exposes `ovl_parameter_redirect_dir[]` for redirect option parsing.
- Defines `struct ovl_opt_set`, which records which dependency-sensitive options were explicitly set by the user.
- Defines `OVL_MAX_STACK` as the maximum number of overlay lower/data layers.
- Defines `struct ovl_fs_context_layer`, pairing a user path name with a resolved `struct path`.
- Defines `struct ovl_fs_context`, the mount-parse staging area.

## Key Structures

`struct ovl_opt_set` tracks explicit user requests for `metacopy`, `redirect`, `nfs_export`, and `index`. This lets verification distinguish explicit conflicts from defaults that can be adjusted automatically.

`struct ovl_fs_context` stores parsed upper and work paths, dynamic lower-layer capacity/counts, data-only lower count, explicit-option flags, an array of lower layers, the original legacy `lowerdir` string, and whether casefold state has been established.

## Exported Functions

- `ovl_init_fs_context()` initializes overlayfs fs-context state.
- `ovl_free_fs()` releases `struct ovl_fs`.
- `ovl_fs_params_verify()` validates and resolves mount config dependencies.
- `ovl_show_options()` renders effective mount options.
- `ovl_xino_mode()` returns the string form of the configured xino mode.

## Integration Notes

`params.c` owns parsing and verification. `super.c` consumes the resulting `struct ovl_fs_context` to construct layers, clone mounts, set fsids, configure root state, and register superblock operations.
