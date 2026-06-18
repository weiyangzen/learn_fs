# File Research: sources/os/linux/linux-stable/fs/nfsd/xdr4.h

Purpose: defines the main NFSD NFSv4 server-side operation model: COMPOUND state, per-operation argument/result structures, XDR encode helpers, pNFS and NFSv4.2 data structures, operation dispatch metadata, and state-management procedure prototypes.

Key structures and state:
- Inline XDR helpers encode bools, 32-bit integers, 64-bit integers, fixed opaque data, and counted opaque/component values, returning NFS status on buffer exhaustion.
- `struct nfsd4_compound_state` tracks current/saved filehandles, replay owner, client/session/slot, minor version, status, current/saved stateids, sid flags, iov/data offsets, and SPO enforcement state.
- Per-operation structs model NFSv4 operations including access, close, commit, create, delegreturn, getattr, link, lock/lockt/locku, lookup, putfh, open/open_confirm/open_downgrade, read, readdir, readlink, remove, rename, secinfo, setattr, setclientid, test/free stateid, get-dir-delegation, verify/write, and release-lockowner.
- NFSv4.1 structures cover exchange-id, sequence, session/clientid destruction, reclaim complete, device IDs, pNFS getdeviceinfo/layoutget/layoutcommit/layoutreturn, and secinfo-no-name.
- NFSv4.2 structures cover allocate/deallocate, clone, copy/offload, seek, offload status, copy notify, and xattr operations.
- `struct nfsd4_copy` carries server-side copy request/response state, flags, callback offload data, source/destination `nfsd_file` refs, async task/list/refcount/TTL state, inter-server copy state, and per-net pointer.
- `struct nfsd4_op` stores op number, status, op descriptor, replay pointer, and a union of all operation payloads.
- `struct nfsd4_compoundargs` and `struct nfsd4_compoundres` hold decode/encode scratch state for one COMPOUND.
- `struct nfsd4_operation` describes dispatch function, release hook, flags, name, response-size estimator, and current-stateid hooks.

Major logic:
- Stateid flag macros mark current and saved stateid presence in compound state.
- Device ID inline helpers encode/decode the 16-byte NFSv4 deviceid layout used by pNFS.
- Copy inline helpers classify copy requests as synchronous/asynchronous and intra/inter-server from flag bits.
- Operation flags describe filehandle requirements, absent-fs allowance, first-op requirements, wrongsec handling, putfh-like behavior, mutating reply-size preflight, DRC cache eligibility, current-stateid clearing, and nontrivial error encoding.
- Declares the main NFSv4 compound decoder/encoder, response-size checks, operation encoder, replay encoder, fattr-to-buffer encoder, and many state/session/open/lock/delegation/clientid handlers implemented elsewhere.

Concurrency and lifetime:
- Compound args carry temporary buffers to free at release time, inline op storage for small compounds, and dynamically allocated op arrays for larger compounds.
- Operation release hooks are part of `struct nfsd4_operation` because many decoded operations own ACLs, strings, exports, file references, lock-denial owners, layout buffers, or async copy state.
- Async copy state uses list linkage, task pointer, refcount, and client/per-net references coordinated by NFSv4 procedure/state code.

Important dependencies:
- Includes `state.h` and `nfsd.h`, and is included widely by NFSv4 proc, XDR, callback, layout, trace, and VFS code.
- Uses kernel NFS protocol constants and NFSD state structures such as clients, sessions, slots, openowners, stateids, callbacks, and `nfsd_file`.

Risk/edge cases:
- The union in `struct nfsd4_op` is the ABI bridge between XDR decode and operation execution; adding operations requires correct release and size-estimation behavior.
- Mutating operations rely on `OP_MODIFIES_SOMETHING` and response-size preflight to avoid performing changes that cannot be encoded.
- NFSv4.1 sessions and v4.0 replay semantics differ, so cacheability flags are delicate.
- Inter-server copy fields combine NFSD state with NFS client-side structures and need strict lifetime handling.
