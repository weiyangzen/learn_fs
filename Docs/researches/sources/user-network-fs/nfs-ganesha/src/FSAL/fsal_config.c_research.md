## sources/user-network-fs/nfs-ganesha/src/FSAL/fsal_config.c

### Purpose
`fsal_config.c` provides small shared accessors over `struct fsal_staticfsinfo_t`. It centralizes how the rest of FSAL code asks whether an FSAL supports features and what configured static limits apply.

### Important APIs, Types, And Functions
The key API is `fsal_supports(struct fsal_staticfsinfo_t *info, fsal_fsinfo_options_t option)`, which maps every known `fso_*` option to fields such as `no_trunc`, `chown_restricted`, `lock_support`, `delegations`, `pnfs_mds`, `pnfs_ds`, `rename_changes_key`, `readdir_plus`, `xattr_support`, and `preserve_unlinked`. Scalar getters expose `maxfilesize`, `maxlink`, `maxnamelen`, `maxpathlen`, `acl_support`, `supported_attrs`, `maxread`, `maxwrite`, `umask`, `expire_time_parent`, and `readdir_mode`.

### Control Flow
The implementation is direct. `fsal_supports` switches on the requested option and returns a boolean derived from the corresponding field or bitmask. Unknown options return false. The scalar functions return fields without validation or clamping.

### State And Persistence
The file is read-only with respect to FSAL state. It does not allocate memory or persist data; callers own and initialize the `fsal_staticfsinfo_t` instance.

### Dependencies And Integration Points
It includes `fsal.h` and `FSAL/fsal_init.h`. `default_methods.c` export capability methods call these helpers through `exp_hdl->fsal->fs_info`. `fsal_helper.c` uses the export methods backed by these helpers to decide whether to permit time setting, link permission behavior, RDMA/zero-copy read buffer ownership, preserved unlink behavior, and other feature-gated flows.

### Risks
Because getters trust `info`, misinitialized FSAL static info propagates directly into protocol behavior. Unknown `fso_*` values fail closed, which is safe for compatibility but can make newly added capabilities appear unsupported until this switch is updated. There is no synchronization here; correctness depends on FSAL static info being immutable or externally protected after initialization.

### Test Signals
Tests should cover every `fso_*` mapping, delegation read/write bit extraction, unknown option false behavior, and that export operations in `default_methods.c` return the same values as these helpers for a populated `fsal_staticfsinfo_t`.
