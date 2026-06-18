# Research: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_LIZARDFS/main.c

Purpose: Registers the LizardFS FSAL module, defines module/export configuration schema, initializes static filesystem capabilities, creates exports, mounts LizardFS client instances, and enables pNFS MDS/DS integration.

Important APIs and types: Global module state is `gLizardFSM`; default capabilities live in `default_lizardfs_info`. Config blocks are `lzfs_fsal_param_block` for module-wide options and `lzfs_fsal_export_param_block` for per-export LizardFS client options. Core functions are `lzfs_fsal_create_export()`, `lzfs_fsal_init_config()`, `init()`, and `finish()`.

Control flow: Module init registers `LizardFS`, installs DS ops, export creation, config init, and pNFS module ops. Config init copies defaults and applies module flags such as pNFS MDS/DS, link/symlink support, fsal trace, grace, and umask. Export creation allocates an export, initializes export ops, parses LizardFS connection/cache settings, mounts a LizardFS instance with `liz_init_with_params()`, attaches the export, optionally creates fileinfo cache and registers a pNFS DS, optionally enables pNFS MDS export ops, fetches root attributes, creates root handle, and sets `op_ctx->fsal_export`.

State and persistence: Exports own mounted LizardFS client state, parsed init params, pNFS flags, root handle, and optional fileinfo cache. Persistent data is in the LizardFS cluster.

Dependencies and integration: Depends on Ganesha config parser, FSAL registration, pNFS DS registry, `context_wrap`, `lzfs_internal`, and LizardFS client initialization. It links module capabilities to object/export ops implemented in other files.

Risks: `lzfs_export->lzfs_params.subfolder` is overwritten with `CTX_FULLPATH(op_ctx)`, ignoring parsed `subfolder` and requiring correct later free ownership. pNFS DS registration uses `export_id` as server id and can collide. Error cleanup has separate `error_pds` and `error` paths that must balance DS refs. Password/md5 config handling is sensitive. Module unregister aborts on failure.

Test signals: Config parsing with required hostname and optional client parameters, delayed init, password/md5 paths, pNFS MDS/DS combinations, duplicate pNFS server ids, root getattr failure cleanup, export release after partial create failure, and module load/unload smoke tests.
