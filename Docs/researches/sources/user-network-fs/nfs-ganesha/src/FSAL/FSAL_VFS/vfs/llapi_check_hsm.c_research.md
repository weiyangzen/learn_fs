# sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_VFS/vfs/llapi_check_hsm.c

Purpose: this file implements the Lustre HSM-aware `check_hsm_by_fd` hook used by FSAL_LUSTRE and dummy-Lustre builds.

Important function: `check_hsm_by_fd` reads `async_hsm_restore` from the current VFS export. If disabled, or if built without `USE_LLAPI`, it returns success. With LLAPI enabled, it calls `llapi_hsm_state_get_fd`, checks `HS_RELEASED`, allocates one-item `hsm_user_request`, gets the file FID with `llapi_fd2fid`, requests `HUA_RESTORE` over the whole file with `llapi_hsm_request`, and returns `ERR_FSAL_DELAY` when a restore is triggered.

Control flow and state: VFS open paths call this hook after opening a fd. A released Lustre file turns an otherwise successful open into a delay/retry signal. The HSM request is submitted to the filesystem root path from `op_ctx->fsal_export->root_fs`.

Dependencies and integration points: depends on Lustre `lustreapi.h` when `USE_LLAPI` is set, FSAL error conversion, and VFS export private config. Plain VFS links a no-op replacement instead.

Risks: memory allocated by `llapi_hsm_user_request_alloc` is not freed in the visible function after request submission or some errors. Error returns from LLAPI are negative errno-style values and are converted with `-rc` in logging/status. Dummy-Lustre builds compile the no-LLAPI path, so HSM restore is silently disabled.

Test signals: `async_hsm_restore` false/true, no-LLAPI build, LLAPI errors from state get/fid/request, released and non-released states, open path mapping of `ERR_FSAL_DELAY` to retry behavior, and request allocation cleanup under sanitizers.
