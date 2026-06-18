# File Research: sources/os/bsd/netbsd-src/sys/fs/nfs/client/nfs_clvfsops.c

## Purpose

Implements VFS operations and mount lifecycle for the new NFS client: mount, old `cmount`, unmount, root vnode lookup, statfs, sync, mount sysctl, forced purge, diskless-root mounting, mount option parsing, and option reporting.

It registers the `nfs` VFS with network and server-boundary flags and wires NFS client initialization/uninitialization through `ncl_init()` and `ncl_uninit()`.

## VFS Registration

The file defines `nfs_vfsops` with:

- `vfs_init = ncl_init`
- `vfs_mount = nfs_mount`
- `vfs_cmount = nfs_cmount`
- `vfs_root = nfs_root`
- `vfs_statfs = nfs_statfs`
- `vfs_sync = nfs_sync`
- `vfs_uninit = ncl_uninit`
- `vfs_unmount = nfs_unmount`
- `vfs_sysctl = nfs_sysctl`
- `vfs_purge = nfs_purge`

It declares module dependencies on `nfscommon`, `krpc`, `nfssvc`, and `nfslock`.

## Mount Sizing

`newnfs_iosize()` clamps read, write, and readdir sizes according to protocol version and transport:

- NFSv4: up to `NFS_MAXBSIZE`
- NFSv3 UDP: up to `NFS_MAXDGRAMDATA`
- NFSv3 TCP: up to `NFS_MAXBSIZE`
- NFSv2: up to `NFS_V2MAXDATA`

It then sets `mnt_stat.f_iosize` to at least page size and `NFS_DIRBLKSIZ`.

## Diskless Root Support

The file supports older and newer diskless boot structures:

- `nfs_convert_oargs()` converts old mount args into `nfs_args`.
- `nfs_convert_diskless()` populates `nfsv3_diskless` from old `nfs_diskless`.
- `nfs_mountroot()` configures the boot network interface, optional MTU, optional default gateway, builds the `server:path` root string, and calls `nfs_mountdiskless()`.
- `nfs_mountdiskless()` duplicates the server sockaddr and delegates to `mountnfs()`.

This path assumes it runs once early in boot before normal concurrent NFS client activity.

## Mount Option Parsing

`nfs_mount()` accepts both old `nfs_args` and newer string options. It filters valid options through `nfs_opts`, then handles:

- cache options: `noac`, `actimeo`, `acregmin/max`, `acdirmin/max`
- transport: `tcp`, `udp`, `mntudp`, `conn`, `noconn`, `resvport`
- protocol: `nfsv3`, `nfsv4`, `minorversion`
- security: `sec=krb5`, `krb5i`, `krb5p`, `principal`, `gssname`, `allgssname`
- behavior: `soft`, `hard`, `intr`, `rdirplus`, `nocto`, `noncontigwr`, `pnfs`
- sizing/retry: `rsize`, `wsize`, `readdirsize`, `readahead`, `wcommitsize`, `timeo`, `timeout`, `retrans`
- name cache: `nametimeo`, `negnametimeo`
- addressing: `from`, `hostname`, `addr`, `fh`, `dirpath`

`nfs_mount_parse_from()` parses `server:path`, bracketed IPv6-style syntax, or deprecated `path@server`, but actual address parsing is IPv4-only via `inet_pton(AF_INET)` and hardcoded port 2049. In the `from` path it currently forces NFSv4 over TCP with no initial filehandle, so `mountnfs()` resolves the directory path.

## Mount Update Behavior

For `MNT_UPDATE`, `nfs_mount()` preserves protocol version, security flavor, lockd strategy, and related immutable flags. It warns if an update changes TCP to UDP because outstanding large TCP RPCs can hang after transfer-size mismatch. Updates call `nfs_decode_args()` and do not enter `mountnfs()`.

## Common Mount Initialization

`mountnfs()` allocates and initializes `struct nfsmount`, including variable trailing storage for Kerberos names, directory path, and server principal. It:

1. Initializes buffer queues and per-mount unique client value.
2. Stores mount user ID for Kerberos state operations when non-root.
3. Copies name/path/security strings into trailing storage.
4. Holds mount credentials and initializes socket request mutexes.
5. Installs helper callbacks `nfs_getnlminfo` and `ncl_vinvalbuf`.
6. Sets default timeouts, retry counts, readahead, and write commit size.
7. Decodes final mount args with `nfs_decode_args()`.
8. Connects the RPC socket with `newnfs_connect()`.
9. For NFSv4.1+, gets a clientid early with `nfscl_getcl()`.
10. For NFSv4 path mounts without a filehandle, resolves the mount directory with `nfsrpc_getdirpath()`.
11. Creates and pins the root nfsnode/vnode.
12. Loads root attributes or fallback attributes.
13. Sets NFSv4 lease/renew values and starts the renew thread for v4.1.
14. Loads NFSv3 fsinfo if applicable.
15. Marks `MNT_NFS4ACLS` when supported attributes advertise ACLs.

On failure, it disconnects the socket, frees credentials/auth, destroys mutexes, removes/free client state if allocated, frees sessions, and releases `nfsmount` plus server sockaddr.

## Argument Normalization

`nfs_decode_args()` applies mount flags to `nfsmount`:

- sets/clears read-only mount flag
- forces sensible TCP timeout/retry behavior
- clears `NFSMNT_NOCONN` for TCP
- clears `RDIRPLUS` for NFSv2
- calculates whether socket reconnect/rebind is required
- clamps timeout/retry values
- rounds read/write sizes down to powers of two above `NFS_FABLKSIZE`
- enforces attr-cache min/max ordering
- clamps readahead
- adjusts write commit size
- reconnects UDP sockets when needed
- stores hostname without trailing path component

## Statfs And Fsinfo

`nfs_statfs()` obtains the root vnode, optionally fetches NFSv3 fsinfo, calls `nfsrpc_statfs()`, refreshes root attributes, loads fsinfo and statfs data into the mount, recomputes I/O size, and maps NFSv4 errors through `nfscl_maperr()`.

`ncl_fsinfo()` is the exported helper for fetching and loading NFSv3 transfer parameters and root attributes.

## Unmount

`nfs_unmount()` handles forced and normal unmount:

- forced unmount cancels outstanding requests and stops NFSv4 renewal first
- flushes vnodes, retrying forced `vflush()` up to 30 times
- normal unmount stops NFSv4 state after vnode flush
- detaches async nfsiod assignments for this mount
- disconnects socket and frees mount credentials, address, auth, mutexes, sessions, and `nfsmount`

## Root, Sync, Sysctl, Purge

`nfs_root()` regets the root nfsnode by mount filehandle, loads NFSv3 fsinfo if still missing, forces `VDIR` when vnode type is unset, and marks `VV_ROOT`.

`nfs_sync()` walks mount vnodes and calls `VOP_FSYNC()` on dirty, unlocked vnodes unless the sync is lazy or forced unmount is underway.

`nfs_sysctl()` supports:

- `VFS_CTL_QUERY`: reports `VQ_NOTRESP` when mount state has `NFSSTA_TIMEO`
- `VFS_CTL_TIMEO`: gets/sets initial timeout warning delay with superuser check

`nfs_purge()` cancels in-flight RPC requests so forced unmount can proceed.

## NLM Integration

`nfs_getnlminfo()` extracts lock-manager information from an NFS vnode:

- filehandle and length
- server sockaddr
- whether the mount is NFSv3
- cached file size
- timeout as timeval

This is installed in `nfsmount::nm_getinfo`.

## Option Reporting

`nfscl_retopts()` serializes active mount options into a caller-provided buffer. It reports protocol version, minor version, pNFS, transport, reserved port, connection mode, hard/soft, interruptibility, close-to-open behavior, noncontiguous writes, lockd state, rdirplus, security flavor, attr-cache timeouts, name-cache timeouts, I/O sizes, readahead, write commit size, timeout, and retransmit count.

## Integration Points

- Calls state code in `nfs_clstate.c`: `nfscl_getcl()`, `nfscl_start_renewthread()`, `nfscl_clientrelease()`, `nfscl_umount()`.
- Calls vnode/node code: `ncl_nget()`, `nfscl_loadattrcache()`, `ncl_vinvalbuf()`.
- Calls RPC code: `newnfs_connect()`, `newnfs_disconnect()`, `nfsrpc_fsinfo()`, `nfsrpc_statfs()`, `nfsrpc_getattrnovp()`, `nfsrpc_getdirpath()`.
- Uses global async I/O daemon assignment arrays under `ncl_iod_mutex`.
- Uses diskless boot data from `nfsdiskless.h`.

## Concurrency Notes

- Mount updates mutate `nfsmount` fields and may reconnect sockets under transport locks.
- `mountnfs()` starts renewal only after mount success is effectively committed.
- `nfs_statfs()` uses `vfs_busy()` around root vnode/statfs work.
- `nfs_unmount()` carefully coordinates forced request cancellation, state teardown, vnode flush, nfsiod detachment, and socket destruction.
- `nfs_sync()` restarts vnode iteration when `vget()` races.

## Risks And Edge Cases

- `from` parsing is IPv4-only despite bracket syntax handling.
- Hardcoded NFS port 2049 in `nfs_mount_parse_from()`.
- Update from TCP to UDP is allowed but explicitly warned as potentially hanging threads.
- Root attribute fallback fabricates permissive directory attributes when getattr fails.
- Error cleanup in `mountnfs()` must stay aligned with every initialized field.
- `nfs_sync()` has a documented racy dirty-buffer count check.
- `nfscl_printopt()`/`nfscl_printoptval()` can truncate silently when buffers are too small.

## Verification Ideas

- Mount option parser tests for old `nfs_args`, `from`, explicit `addr`/`fh`, invalid numeric values, security names, and update immutability.
- Failure-injection tests for each `mountnfs()` stage to verify cleanup.
- Diskless-root tests for interface setup, gateway setup, and root path construction.
- Forced unmount tests with outstanding RPCs and assigned nfsiod workers.
- Statfs tests with missing fsinfo, NFSv4 error mapping, and fallback root attributes.
