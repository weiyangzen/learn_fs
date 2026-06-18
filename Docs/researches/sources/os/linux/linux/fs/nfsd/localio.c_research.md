# File Research: sources/os/linux/linux/fs/nfsd/localio.c

Read completely: 217 lines.

NFSD support for NFS LOCALIO, allowing a local kernel NFS client to bypass the network stack after proving that the server is local.

Key responsibilities:
- Implements `nfsd_open_local_fh`, converting an NFS filehandle into `svc_fh`, mapping client credentials to service credentials, and acquiring an `nfsd_file` through `nfsd_file_acquire_local`.
- Caches the acquired local `nfsd_file` in an RCU pointer supplied by the client, using compare-exchange to handle concurrent installers and paired net/file references.
- Exposes file pointer and DIO alignment accessors through `nfsd_localio_operations`.
- Installs NFSD LOCALIO operations by assigning `nfs_to`.
- Implements a hidden LOCALIO RPC version with NULL and `UUID_IS_LOCAL`; the UUID procedure records local clients in `nfsd_net.local_clients`.
- Decodes UUID arguments from fixed opaque XDR.

Important interactions:
- Uses `nfsd_net_try_get`/`nfsd_net_put` to keep the server net namespace alive for local file references.
- Uses `svcauth_map_clnt_to_svc_cred_local` and the filecache local-acquire path.
- Depends on `CONFIG_NFS_LOCALIO` fields in `nfsd_net`.

Notable risks:
- LOCALIO bypasses normal network transport and request authorization paths; correctness depends on credential mapping and auth-domain validation.
- The cached pointer owns both file and net lifetime; losing those paired references would create leaks or use-after-free risk.
