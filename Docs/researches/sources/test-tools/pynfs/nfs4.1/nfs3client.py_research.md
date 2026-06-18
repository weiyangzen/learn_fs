# sources/test-tools/pynfs/nfs4.1/nfs3client.py

## Purpose
`nfs3client.py` is a lightweight RPC client stack for NFSv3 and mount/portmap services. It is primarily used by pNFS data-server support to access NFSv3-backed data servers with a uniform procedural API.

## Important APIs, Types, And Functions
- `PORTMAPClient` calls the portmapper and provides `get_port(prog, vers)`.
- `Mnt3Client` calls the MOUNT v3 service and provides `get_rootfh(export)`.
- `NFS3Client` calls the NFS v3 service, owns a `Mnt3Client`, stores a verifier, and exposes `null`, `proc_async`, `proc`, and `listen`.
- Module-level `op3 = nfs_ops.NFS3ops()` builds generated NFSv3 procedure argument objects.

## Control Flow
Each client subclass derives from `rpc.Client`, stores a target server address, lazily establishes an RPC pipe with `get_pipe`, packs generated argument objects using the appropriate generated packer, sends calls, listens for replies, and unpacks the expected generated result type.

`NFS3Client.__init__` uses `PORTMAPClient` to discover mountd and NFS ports unless a port is supplied, creates a `Mnt3Client`, and records callback/control metadata. `proc` sends a request and derives the result class name from the argument class name by replacing `3args` with `3res`. Optional summary output records operation names and returned `nfsstat3` strings.

## State And Persistence Behavior
State is limited to RPC pipes, server addresses, credentials, discovered ports, verifier, and summary object. NFS filehandles and server-side data are external. `get_pipe` reconnects when the stored pipe is missing or inactive.

## Dependencies And Integration Points
The module depends on generated NFSv3, MOUNTv3, and PORTMAP XDR constants/types/packers, `rpc.rpc`, `nfs_ops`, `nfs4lib`, `threading`, `hmac`, and `os.path`. `dataserver.DataServer3` uses it for NFSv3-backed pNFS file layout operations.

## Risks And Edge Cases
- `Mnt3Client.get_rootfh` builds `dirpath('/' + os.path.join(*export))`; an empty export list or bytes components can fail.
- `PORTMAPClient.proc` requires an explicit `restypename`, while NFS3 `proc` derives it; misuse is easy.
- `listen` assumes any nonempty response data can be unpacked into the expected result type.
- Imported modules such as `threading`, `hmac`, and `traceback` are mostly unused here, suggesting copy/paste surface.
- `NFS3Client.set_cred` only changes `default_cred`; existing in-flight calls keep their original credentials.

## Test Signals
Signals include portmap lookup, mount root filehandle acquisition, NULL calls, each packed NFSv3 operation returning the matching generated result type, summary logging, reconnect behavior after inactive pipes, and integration with `DataServer3` create/read/write/truncate/getattr paths.
