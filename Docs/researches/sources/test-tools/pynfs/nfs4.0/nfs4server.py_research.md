# sources/test-tools/pynfs/nfs4.0/nfs4server.py

## Purpose
`nfs4server.py` is a small Python NFSv4.0 server implementation used by pynfs test tooling. It subclasses `rpc.RPCServer`, decodes NFS COMPOUND calls, dispatches each operation to an `op_*` method, and uses `nfs4state` for the virtual filesystem, client IDs, open state, lock state, share reservations, stateid sequencing, and replay handling. It is intentionally incomplete in some protocol areas, with explicit stubs for delegation, openattr, release lockowner, and partial SECINFO behavior.

## Important APIs, Types, And Functions
- `verify_name(name)` enforces component name policy: empty names are `NFS4ERR_INVAL`, names longer than `NFS4_FHSIZE` are `NFS4ERR_NAMETOOLONG`, `"."`/`".."`
  are `NFS4ERR_BADNAME`, configured characters such as `/`, `~`, and `#` are `NFS4ERR_BADCHAR`, and invalid UTF-8 is `NFS4ERR_INVAL`.
- `verify_utf8(str)` uses `codecs.utf_8_decode` as the common tag/name validation primitive.
- `simple_error(error, *args)` uses the caller's `op_*` name to construct the matching `*_4res` and `nfs_resop4` wrapper. This keeps operation handlers compact but tightly couples handler names to generated XDR class names.
- `NFS4Server.__init__(rootfh, host, port, pubfh=None)` wires packers/unpackers, `NFSServerState`, filehandle cache, root/public handles, and verifier counter.
- `handle_0()` implements NULL RPC, including limited RPCSEC_GSS proc handling.
- `handle_1()` unpacks a COMPOUND request, calls `O_Compound`, packs `COMPOUND4res`, and returns an RPC success or XDR garbage result.
- `O_Compound()` validates minor version and UTF-8 tag, resets per-compound current/saved handles, sequentially dispatches opcodes through `nfs_opnum4`, stops at first NFS error, and returns the result array.
- `op_access`, `op_getattr`, `op_getfh`, `op_lookup`, `op_lookupp`, `op_putfh`, `op_putrootfh`, `op_savefh`, and `op_restorefh` implement basic filehandle and attribute flow.
- `op_create`, `op_open`, `op_close`, `op_open_confirm`, `op_open_downgrade`, `op_read`, `op_write`, `op_commit`, `op_lock`, `op_lockt`, `op_locku`, `op_remove`, `op_rename`, and `op_link` are the main stateful filesystem operations.
- `op_setclientid` and `op_setclientid_confirm` implement the client ID handshake over `NFSServerState.confirmed` and `.unconfirmed`.
- `startup(host, port)` builds a `VirtualHandle` root, registers with portmap if possible, and starts the RPC server loop.

## Control Flow
A TCP NFS request enters `handle_1`, which resets the `FancyNFS4Unpacker`, delegates protocol logic to `O_Compound`, and packs the resulting `COMPOUND4res`. `O_Compound` unpacks the whole request, rejects minor versions other than zero and invalid UTF-8 tags, then initializes `curr_fh` and `saved_fh` for the compound. For each `nfs_argop4`, it maps the numeric opcode to a generated name such as `OP_OPEN`, lowercases that name into a method such as `op_open`, executes it, appends the returned `nfs_resop4`, and stops on the first non-OK status. Individual handlers return through `simple_error`, so the dispatch loop only deals with uniform `(status, result_op)` tuples.

Stateful operations first validate replay sequence IDs via `self.state.check_seqid`. If a replay is detected, `check_replay` compares the newly packed operation to the cached operation and either returns the cached result or `NFS4ERR_BAD_SEQID`. Non-replay mutations call `self.state.advance_seqid` after success or after sequence-consuming errors so repeated requests can be answered consistently.

Filesystem control flow is filehandle-centered. `PUTROOTFH`, `PUTPUBFH`, and `PUTFH` set `curr_fh`; `SAVEFH` snapshots it for later `LINK`/`RENAME`; `RESTOREFH` restores it. `GETFH` inserts the current in-memory handle into `fhcache` before returning its opaque bytes; `PUTFH` can only resolve handles previously cached this way. `LOOKUP` and `LOOKUPP` replace `curr_fh` with child/parent virtual handles. `CREATE`, `REMOVE`, `RENAME`, and `LINK` mutate `VirtualHandle` directory entries and return `change_info4` derived from the directory change counters.

Open control flow validates client ID confirmation, owner sequence, current directory, claim type, target name, and open/create mode. It handles `OPEN4_CREATE` with `EXCLUSIVE4`, `GUARDED4`, and unchecked/create-attrs behavior, then delegates share reservation and stateid generation to `NFSServerState.open`. Delegations are always returned as `OPEN_DELEGATE_NONE`. `CLOSE`, `OPEN_CONFIRM`, and `OPEN_DOWNGRADE` translate stateids and update cached state through `NFSServerState`.

Read/write/control operations validate current filehandle type and stateid access. `READ`, `WRITE`, and `SETATTR(size)` call `NFSServerState.check_read` or `check_write` before touching file data. `COMMIT` validates regular-file type and offset/count overflow but returns the in-memory `write_verifier`; comments explicitly state the RAM-backed server pretends operations are `FILE_SYNC4`.

## State And Persistence Behavior
The server has no durable storage by default. `startup` uses `nfs4state.VirtualHandle`, which stores directories, file data, attributes, link counts, ACLs, and locks in memory. Restarting loses the file tree, client IDs, filehandle mappings, and all open/lock state. `fhcache` is also process-local and is only populated by `GETFH`, which the source comments identify as incomplete for handles embedded in GETATTR or READDIR results.

Persistent-looking protocol state is simulated in `NFSServerState`: server instance bytes, generated client IDs, setclientid verifiers, open owner/lock owner sequence numbers, cached replay responses, stateids, share reservations, lock ranges, and lease timestamps. `write_verifier` and `nextverf()` are generated from process time and a local counter.

## Dependencies And Integration Points
The module depends on generated XDR constants and types from `xdrdef.nfs4_const`, `xdrdef.nfs4_type`, and `xdrdef.nfs4_pack`, pynfs helpers in `nfs4lib`, RPC infrastructure in `rpc.rpc`/`rpc.portmap`, and implementation state in `nfs4state`. It is executable as a server script and adjusts `sys.path` when run from the package root. The server is implicitly exercised by the `servertests` modules through `NFS4Client` operations that expect RFC3530-style NFSv4.0 behavior.

## Risks And Edge Cases
- The shebang says Python 3, but the file contains Python 2 constructs and imports (`StringIO`, `print` statements without parentheses in places, `long` indirectly through `nfs4state`), so runtime compatibility depends on the larger pynfs conversion state.
- `simple_error` relies on generated globals and caller naming conventions; a renamed handler or missing generated class becomes a runtime `RuntimeError`.
- `op_access` computes invalid bits with `all = ~valid_mask`; Python's unbounded negative integers make expression precedence and bit handling sensitive.
- Filehandle cache behavior is explicitly incomplete and can produce `NFS4ERR_BADHANDLE` for handles not first seen through `GETFH`.
- Many RFC details are stubs or simplified: delegations, open attributes, release lockowner, SECINFO, access control, callback principals, and stable storage semantics.
- `op_setclientid_confirm` implements noted departures from RFC logic and assumes a single matching entry by client owner string.
- Several operations check type and names but not real permissions; comments mark access checking as TODO around remove/rename/link.

## Test Signals
This file is directly targeted by the server tests in this group: ACCESS verifies invalid masks and no-current-filehandle behavior; CREATE/LINK/GETFH/GETATTR/COMMIT/CLOSE/LOCK/LOCKT verify operation-level status returns; COMPOUND verifies minor versions, tags, illegal op packing, and long sequences; delegation and GSS tests exercise unsupported or surrounding RPC/security behavior. The strongest test signals are expected NFS status codes, replay sequence behavior, stateid transitions, and `change_info4`/attribute effects observed through client compounds.
