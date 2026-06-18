# sources/test-tools/pynfs/nfs4.1/dataserver.py

## Purpose
`dataserver.py` manages pNFS data-server access for the NFSv4.1 test server. It abstracts active data servers, opens backing files derived from MDS filehandles, reads/writes/truncates data through NFSv4.1 or NFSv3 clients, and builds file-layout device address bodies used by MDS layout responses.

## Important APIs, Types, And Functions
- `DataServer(server, port, path, flavor=AUTH_SYS, active=True, mdsds=True, multipath_servers=None, summary=None)` stores endpoint/path state and controls activation.
- `DataServer.up()`, `down()`, `reset()`, `get_netaddr4()`, `get_multipath_netaddr4s()`, and `fh_to_name()` provide common lifecycle, device-address, and name-mapping behavior.
- `DataServer41` connects to an NFSv4.1 DS, creates a client/session, ensures the root path exists, and implements `open_file`, `close_file`, `read`, `write`, `truncate`, and `get_size`.
- `DataServer3` connects through portmap and mountd, uses NFSv3 CREATE/LOOKUP/READ/WRITE/SETATTR/GETATTR, and implements the same high-level file API with no open stateid.
- `DSDevice` loads data-server configuration files, stores active server objects, packs `nfsv4_1_file_layout_ds_addr4`, and dispatches open/close/filehandle retrieval across active data servers.

## Control Flow
`DSDevice.load(filename, server_obj)` parses each non-comment line with `nfs4lib.parse_nfs_url`, treats the last server tuple as the direct endpoint, treats earlier tuples as multipath alternates, constructs `DataServer41` entries, and exits on parse/connect failure. After loading, it computes `address_body` by packing stripe indices and multipath netaddr lists.

For NFSv4.1 data servers, `connect` creates AUTH_SYS root credentials, instantiates `NFS4Client`, runs NULL, performs `EXCHANGE_ID` through `new_client`, creates a session with broad channel attrs, and sends `RECLAIM_COMPLETE`. `make_root` walks the configured path, creating missing directories, gets the root filehandle, and verifies read/lookup/modify/extend access. `open_file` hashes the MDS filehandle into a name, attempts guarded create/open, falls back to `OPEN4_NOCREATE` on `NFS4ERR_EXIST`, and caches `(ds_fh, open_stateid)` by MDS filehandle.

For NFSv3 data servers, `connect` locates mount and NFS ports, gets the export root filehandle, and verifies ACCESS. `open_file` attempts guarded CREATE and falls back to LOOKUP on existing files. Read/write/truncate/size methods map directly to NFSv3 procedures.

## State And Persistence Behavior
Each `DataServer` tracks active state, endpoint fields, root/path filehandle, and a `filehandles` map keyed by MDS filehandle. Backing file contents are persisted by the external DS server, not by this module. `DSDevice.address_body` is cached after load and must be refreshed when active servers or multipath addresses change. NFSv4.1 DS sessions are reset on state errors such as stale client ID or bad/dead session.

## Dependencies And Integration Points
The module depends on `rpc.rpc`, `nfs4client`, `nfs3client`, generated NFSv4/NFSv3 types and constants, `nfs_ops`, `nfs4lib`, `NFS4Packer`, `hashlib`, `socket`, and the pNFS file-layout classes in `fs.py`. `FSLayoutFSObj` calls `DSDevice.open_ds_file`, `close_ds_file`, and `get_ds_filehandles`; `FilelayoutVolWrapper` calls per-DS read/write/truncate/size methods.

## Risks And Edge Cases
- `DataServer.fh_to_name` hashes a Python `"%r"` string without encoding; under Python 3 `hashlib.sha1` expects bytes.
- `DataServer41._execute` logs `nfsstat4` without importing it into the module namespace; it imported `const4.nfsstat4`.
- `close_file` for NFSv4.1 uses `seqid=0` with a FIXME that it must not always be zero.
- `DataServer41.write` and `DataServer3.write` ignore result details and short-write semantics.
- `make_root` has comments noting DS directories are not cleaned.
- `DSDevice.load` exits the whole process on configuration/connect errors rather than reporting recoverable failures.
- `get_ds_filehandles` assumes every active DS has already opened the file and stored a mapping.

## Test Signals
Signals include successful parsing of single and multipath DS URLs, correct packed device address bodies, NFSv4.1 reset on session/client state errors, DS root creation/access validation, stable MDS-fh-to-DS-fh mapping, file-layout open/close hooks creating and deleting DS file mappings, and read/write/truncate operations reflected through layout-backed files.
