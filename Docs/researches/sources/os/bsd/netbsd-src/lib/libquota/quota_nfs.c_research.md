# File Research: sources/os/bsd/netbsd-src/lib/libquota/quota_nfs.c

This file implements read-only NFS quota retrieval through the rquota RPC protocol. It scales remote rquota block values by the server-provided block size into DEV_BSIZE units and maps zero remote limits to `QUOTA_NOLIMIT`; nonzero limits are stored as remote value minus one, matching the library convention used elsewhere.

`rquota_to_quotavals` converts one `struct rquota` into separate block and inode `quotaval` records, setting expire times as current time plus server time-left values and grace to `QUOTA_NOTIME`. `callaurpc` resolves the host with `gethostbyname`, creates a UDP RPC client, installs default authunix credentials, and calls the requested procedure with a 25-second total timeout.

`__quota_nfs_get` validates id type as user or group and object type as blocks or files, then splits the mount device string as `host:path`. It first tries extended rquota version `EXT_RQUOTAVERS`, including group quota support. If the server reports version mismatch or no registered program and the request is for user quotas, it falls back to old `RQUOTAVERS`.

RPC failures are translated for convenience: unreachable or unsupported cases can become `ENOENT`. Rquota status `Q_NOQUOTA` returns a cleared quota value, `Q_EPERM` becomes `EACCES`, `Q_OK` returns either the converted block or file quota, and unknown status becomes `ERANGE`.
