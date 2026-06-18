# File Research: sources/os/linux/linux/fs/nfsd/xdr4.h

`xdr4.h` is the main NFSv4 server-side operation type header. It defines compound request/response state, per-operation argument/result structures, inline XDR encode helpers, operation dispatch metadata, state/session prototypes, and v4.1/v4.2 extension types.

Key elements:
- Encoding helpers: inline bool, uint32, uint64, fixed opaque, and variable opaque encoders return `nfs_ok` or `nfserr_resource`.
- `struct nfsd4_compound_state` tracks current/saved filehandles, replay owner, client, session/slot, data offset, iov count, minor version, status, current/saved stateids, and stateid presence flags.
- `struct nfsd4_op` stores op number, status, descriptor, replay info, and a large union of every v4 operation’s decoded state.
- `struct nfsd4_compoundargs` and `struct nfsd4_compoundres` are the XDR decode/encode scratch objects used per compound.
- `enum nfsd4_op_flags` describes operation constraints: no filehandle required, absent filesystem allowed, first-op-only, wrongsec handling, PUTFH-like, modifies something, DRC cache eligibility, stateid clearing, and nontrivial error encoding.
- `struct nfsd4_operation` binds an op implementation to release, flags, name, reply-size estimator, and current-stateid accessors.

Covered operation families:
- Base v4: access, close, commit, create, delegreturn, getattr, link, lock/lockt/locku, lookup, open/open-confirm/open-downgrade, putfh, read, readdir, readlink, remove, rename, secinfo, setattr, setclientid, verify/nverify, write, release lockowner.
- v4.1/session/pNFS: exchange_id, backchannel_ctl, bind_conn_to_session, create/destroy session, destroy clientid, sequence, reclaim_complete, test/free stateid, directory delegation, getdeviceinfo, layoutget/commit/return, secinfo_no_name.
- v4.2: allocate/deallocate, clone, copy, offload status, copy notify, seek, and xattr get/set/list/remove.

Notable structures include `nfsd4_open`, `nfsd4_readdir` with case-attribute cache, layout/deviceid helpers, copy/offload structures with async state and callback result fields, and NFSv4 callback recall-any data.

This header is a dense protocol contract: it does not execute operations, but it defines the data shape and dispatch hooks used by NFSv4 decode, operation processing, state management, and encode paths.
