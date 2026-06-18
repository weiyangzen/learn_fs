# File Research: sources/os/linux/linux-stable/fs/nfsd/localio.c

## Summary
Implements NFSD support for local NFS clients to bypass the network stack while still using NFSD authorization and filecache machinery.

## Main APIs
- `nfsd_localio_ops_init()` installs `nfsd_localio_operations`.
- Hidden RPC version `localio_version1` provides `NULL` and `UUID_IS_LOCAL`.
- Internal `nfsd_open_local_fh()` maps a client NFS filehandle to an `nfsd_file`.

## Behavior
`nfsd_open_local_fh()` validates a filehandle, pins the NFSD net namespace, reuses an already installed local `nfsd_file` if present, maps client credentials into `svc_cred`, and calls `nfsd_file_acquire_local()`. On success it installs the file with `cmpxchg()` so concurrent local opens share it. `UUID_IS_LOCAL` records whether a client UUID is local in the per-net local-client list.

## Risks
Localio deliberately bypasses connection-based authorization and crosses client/server kernel contexts, so its security depends on correct credential mapping and net-namespace lifetime handling. The installed RCU pointer carries both file and net references that must be released in the matching local put path.
