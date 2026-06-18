# File Research: sources/os/linux/linux/fs/overlayfs/params.c

## Purpose

`params.c` implements overlayfs mount parameter parsing, fs-context initialization/freeing, option dependency verification, reconfigure behavior, and mount option rendering for `/proc/mounts`.

## Main Responsibilities

- Define overlayfs module parameters and default mount-option modes.
- Declare the `fs_parameter_spec` table for old and new mount APIs.
- Parse legacy comma-separated mount data with overlay-specific escaping.
- Parse `lowerdir=`, `lowerdir+`, `datadir+`, `upperdir=`, and `workdir=` layer options.
- Validate layer paths as directories and reject unsupported dentries.
- Enforce consistent casefold state across all layers.
- Maintain `struct ovl_fs_context` lower-layer arrays and path ownership.
- Resolve feature dependencies among redirect, metacopy, index, NFS export, verity, userxattr, UUID, and volatile mode.
- Allocate and initialize `struct ovl_fs` and fs-context private state.
- Free untransferred mount context state on failure.
- Render effective mount options.

## Parameter Model

The file supports these major options:

- layer paths: `lowerdir`, `lowerdir+`, `datadir+`, `upperdir`, `workdir`
- behavior flags: `default_permissions`, `userxattr`, `volatile`, `override_creds`
- mode options: `redirect_dir`, `index`, `uuid`, `nfs_export`, `xino`, `metacopy`, `verity`, `fsync`

`lowerdir=` supports colon-separated lower layers and double-colon-separated data-only layers, for example `lower1:lower2::data1::data2`. `lowerdir+` and `datadir+` are new API forms that can accept file descriptors as well as strings.

## Important Functions

- `ovl_next_opt()` parses old mount option strings while respecting backslash-escaped commas.
- `ovl_parse_param_split_lowerdirs()` splits legacy `lowerdir=` strings and validates colon sequencing.
- `ovl_mount_dir()` and `ovl_mount_dir_noesc()` resolve path strings.
- `ovl_mount_dir_check()` validates directory-ness, casefold consistency, weird dentry rejection, read-only upper rejection, and lower/data ordering constraints.
- `ovl_ctx_realloc_lower()` grows the parsed lower-layer array up to `OVL_MAX_STACK`.
- `ovl_add_layer()` transfers parsed path/name ownership into config or lower-layer context slots.
- `ovl_parse_layer()` handles both string and file-descriptor layer options.
- `ovl_parse_param_lowerdir()` replaces existing lower layers and parses legacy lower/data lower syntax.
- `ovl_parse_param()` handles all fs parameters and stores explicit-option bits in `ctx->set`.
- `ovl_init_fs_context()` allocates context state and sets defaults from module parameters and Kconfig.
- `ovl_free_fs()` releases overlayfs superblock-private resources when mount setup fails or the superblock is destroyed.
- `ovl_fs_params_verify()` resolves cross-option dependencies and permission constraints.
- `ovl_show_options()` prints the effective option set.

## Option Dependency Rules

`ovl_fs_params_verify()` applies several important rules:

- `workdir` and `index=on` are ignored without an upperdir.
- `volatile` is meaningless without an upperdir and is reset to the default.
- `uuid=on` without upperdir falls back to `uuid=null`.
- `metacopy=on` requires `redirect_dir=on`; explicit conflicts fail, while implicit defaults may be adjusted.
- `nfs_export=on` requires index support except in lower-only conditions that require `redirect_dir=nofollow`.
- `nfs_export=on` conflicts with metacopy and verity combinations.
- `userxattr` forces redirect and metacopy off unless explicitly requested in conflicting ways.
- Without `userxattr`, unprivileged callers cannot explicitly request trusted-xattr-dependent redirect, metacopy, verity, or data-only lower layers.

## Mount Context Lifetime

`ovl_init_fs_context()` allocates `struct ovl_fs_context`, preallocates three lower slots, allocates `struct ovl_fs`, sets defaults, installs fs-context operations, and initializes the whiteout mutex.

`ovl_free()` frees the overlayfs private state if it has not been transferred to the superblock and frees parsed path context state. `ovl_free_fs()` releases traps, dentries, in-use locks, cloned mounts, anonymous devices, config strings, credentials, and layer arrays.

## Reconfigure Behavior

`ovl_reconfigure()` preserves old mount API behavior by ignoring remount options. For the new mount API, it rejects option changes. It also prevents remounting read-write when the overlay is forced read-only, and syncs the upper filesystem when transitioning to read-only if needed.

## Risk Notes

- Legacy `lowerdir=` parsing has subtle escaping and colon semantics; incorrect parsing can reorder data-only layers.
- Dependency resolution changes effective options, so `/proc/mounts` must show final config rather than raw user input.
- `override_creds` changes the creator credential used for overlay operations and is restricted to the fsopen user namespace.
- Casefold consistency is enforced at mount parsing and later rechecked during lookup.
