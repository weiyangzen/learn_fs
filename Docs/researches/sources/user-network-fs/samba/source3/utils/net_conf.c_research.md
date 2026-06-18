# sources/user-network-fs/samba/source3/utils/net_conf.c

Purpose: implements `net conf`, a local libsmbconf interface for registry-backed Samba configuration and file-backed imports.

Important APIs/types/functions: `net_conf()` dispatches a private `conf_functable` through `net_conf_run_function()`. `net_conf_wrap_function()` opens `registry:`, calls handlers, and shuts down. Handlers cover list/import/listshares/drop/showshare/addshare/delshare/setparm/getparm/delparm/getincludes/setincludes/delincludes.

Control flow: handlers validate usage and operate on `struct smbconf_ctx`. Import opens `file:<filename>`, optionally selects one service, test-prints when requested, otherwise uses transactions, drops existing config for full import, and commits in batches. Addshare validates name/path, creates the share, sets path/comment/guest/writeable, then commits. Setparm lowercases and validates the parameter, creates a missing service, and sets it transactionally.

State and persistence: mutates registry-backed Samba configuration. `drop` deletes all config. `delshare` also deletes share security. Include operations mutate include lists. Import test mode avoids writes.

Dependencies/integration: depends on libsmbconf, registry smbconf backend, loadparm, `net_conf_util.h`, `delete_share_security()`, and `net_context` options like `opt_testmode`.

Risks: destructive operations can remove production config or ACLs. Import batching commits on `sidx % 100 == 0`, including the first item, and deserves regression coverage. `setparm` can create a typo service. Validation is delegated to `net_conf_param_valid()`. Include mutations are not explicitly transaction-wrapped.

Test signals: list/show/listshares; full and single-service import with/without `--test`; rollback on invalid import; addshare invalid name/path and homes empty path; set/get/del parameter; include get/set/delete; delshare ACL cleanup errors.
