# sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_RGW/main.c

This file registers the RGW FSAL module, parses module/export configuration, initializes librgw once, mounts an RGW filesystem per export, creates the root handle, and unregisters/shuts down the module at unload.

The singleton `RGWFSM` defines static FSAL capabilities: large file size, 1024 name/path length, no links/symlinks/locks, named attributes, unique handles, settable times, optional xattrs, computed readdir cookies, and chunked readdir. `rgw_items` configures global Ceph options (`ceph_conf`, `name`, `cluster`, `init_args`, `umask`). Export params require `user_id`, `access_key_id`, and `secret_access_key`. `init_config` loads module config and displays fs info. `create_export` performs lazy `librgw_create` under `init_mtx`, parses export credentials, calls `rgw_mount` or optional `rgw_mount2`, attaches the export, registers invalidation upcalls, fetches root attributes, constructs the root handle, and sets `op_ctx->fsal_export`. `init` registers the FSAL and installs module/handle ops. `finish` unregisters and calls `librgw_shutdown`.

State persistence is external to Ceph RGW. This file owns process lifetime for the librgw instance and per-export mount handles. The root handle is held in `struct rgw_export` and normal object persistence is represented by librgw handles.

Dependencies include Ganesha config parsing, FSAL registration, export manager context, common allocation, and librgw. Integration points are the `MODULE_INIT`/`MODULE_FINI` symbols, `fsal_attach_export`, invalidation registration, and `handle_ops_init`.

Risks include incomplete cleanup on several `create_export` error paths, logging but continuing when `ceph.conf` is missing, module-global initialization races if `librgw_create` fails, and credential requirements that must match RGW auth behavior. Test signals should cover config validation, failed librgw init, bad credentials, repeated exports, mount2 path cases, root getattr failures, invalidation registration failure, and module unload after partially initialized exports.
