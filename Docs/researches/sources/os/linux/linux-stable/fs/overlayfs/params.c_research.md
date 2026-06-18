# File Research: sources/os/linux/linux-stable/fs/overlayfs/params.c

## Purpose

`params.c` implements overlayfs mount parameter parsing, fs-context setup/freeing, remount behavior, option verification, and `/proc/mounts` option rendering.

## Main Responsibilities

- Define module defaults for redirect, xino, index, NFS export, and metacopy.
- Define fs parameter specs for legacy and new mount APIs.
- Parse `lowerdir`, `lowerdir+`, `datadir+`, `upperdir`, `workdir`, and feature options.
- Resolve file/string layer inputs into paths and store display names.
- Enforce layer ordering and casefold consistency while parsing.
- Verify cross-option constraints after parsing.
- Free fs-context and overlayfs mount state on failure.
- Render effective mount options with `ovl_show_options()`.

## Parsing Details

`ovl_parameter_spec[]` accepts:

- `lowerdir`
- `lowerdir+`
- `datadir+`
- `upperdir`
- `workdir`
- `default_permissions`
- `redirect_dir`
- `index`
- `uuid`
- `nfs_export`
- `userxattr`
- `xino`
- `metacopy`
- `verity`
- `fsync`
- `volatile`
- `override_creds`

Legacy monolithic parsing uses `ovl_next_opt()` to split comma-separated options while honoring escaped commas.

`ovl_parse_param_lowerdir()` handles colon-separated legacy `lowerdir=`. Single `:` separates merged lower layers; double `::` transitions into data-only layers. It rejects malformed colon sequences, trailing colons, too many layers, regular lower layers after data layers, and appending via a leading colon.

`ovl_parse_layer()` supports both string paths and file parameters. New `lowerdir+` and `datadir+` use unescaped path lookup, while legacy `lowerdir` supports backslash unescaping.

## Layer Validation

`ovl_mount_dir_check()` ensures parsed paths are directories, are not weird/unsupported dentries, and have consistent casefold state across all layers. For upper/work paths, it rejects read-only mounts and unsupported `DCACHE_OP_REAL` upper filesystems. For lower additions, it enforces `OVL_MAX_STACK`, prevents mixing legacy `lowerdir` with new add options, and prevents regular lowers after data lowers.

## Option Verification

`ovl_fs_params_verify()` normalizes and rejects incompatible feature combinations:

- `workdir` and `index=on` are ignored without upperdir.
- `volatile` is meaningless without upperdir.
- `uuid=on` without upperdir falls back to `uuid=null`.
- `metacopy=on` requires `redirect_dir=on`, unless explicit conflicting options require disabling or erroring.
- `nfs_export=on` requires index and conflicts with metacopy/verity.
- `userxattr` disables default redirect/metacopy behavior and rejects explicit incompatible options.
- Without trusted-xattr privileges, explicit redirect/metacopy/verity/data-only lower requests are rejected unless `userxattr` is used.

## Context Lifecycle

`ovl_init_fs_context()` allocates `struct ovl_fs_context`, default lower capacity, and `struct ovl_fs`, installs default feature modes, sets fs-context operations, and initializes the whiteout mutex.

`ovl_free()` frees untransferred overlay state and fs-context layer paths/names. `ovl_free_fs()` releases traps, dentries, locks, mounts, pseudo devices, config strings, creator credentials, and the overlay fs object.

`ovl_reconfigure()` largely preserves historical remount behavior, allowing old API options to be ignored but rejecting new mount API changes. It forces read-only consistency and syncs upper fs when transitioning to read-only if required.

## Option Display

`ovl_show_options()` prints the effective lower/upper/work options and only prints feature options when they differ from defaults or are explicitly relevant. It distinguishes legacy `lowerdir` from `lowerdir+`/`datadir+`.

## Dependencies And Integration

`params.c` feeds `super.c` through `struct ovl_fs_context` and `struct ovl_config`. It relies on `overlayfs.h` feature helpers, `ovl_dentry_casefolded()`, `ovl_dentry_weird()`, and `ovl_free_fs()`.

## Risk Notes

- Mount option interactions are feature-critical; a permissive fallback can silently disable index/NFS/xino semantics.
- Escaping and `:` parsing in `lowerdir=` is compatibility-sensitive.
- `override_creds` changes creator credentials and must remain aligned with user namespace checks in `super.c`.
