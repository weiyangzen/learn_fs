## sources/user-network-fs/samba/source3/lib/sysquotas_nfs.c

Purpose: NFS quota backend using the remote rquota RPC protocol. It supports reading user quotas from an NFS server and explicitly does not support setting quotas.

Important functions are XDR helpers `my_xdr_getquota_args`/`my_xdr_getquota_rslt`, exported `sys_get_nfs_quota`, and `sys_set_nfs_quota`. It consumes an NFS device string of the form `host:/export/path` and returns `SMB_DISK_QUOTA`.

Control flow: get validates inputs and only accepts `SMB_USER_QUOTA_TYPE`. It splits `bdev` at `:`, uses the host to create a UDP RPC client for `RQUOTAPROG/RQUOTAVERS`, authenticates with `authunix_create_default`, calls `RQUOTAPROC_GETQUOTA` with a two-second timeout, decodes rquota status and fields, maps status 1 to quota values, status 2 to no-limit quota, and status 3 to `EPERM`. `ECONNREFUSED` from the RPC call is treated as success/no quotas. Cleanup destroys auth/client handles and frees the host buffer.

State and persistence: read-only; no local persistent state. Dependencies are SunRPC headers/libraries, `rpcsvc/rquota.h`, Samba quota structs, and memory/debug helpers.

Risks: only UDP rquota v1 is used, with a fixed short timeout. Only user quotas are supported; group/fs quota types return `ENOSYS`, and set always returns `ENOSYS`. Device-string parsing is fragile for unusual NFS mount source syntax. Tests should cover status-code mapping, connection refused behavior, malformed `host:path`, unsupported quota types, and cleanup on RPC/auth failures.
