# File Research: sources/os/bsd/dragonflybsd/sys/vfs/nfs/nfsrvcache.h

## Purpose

`nfsrvcache.h` defines the server recent-request cache entry structure, cache size bounds, states, return codes, and flags used to suppress duplicate NFS request execution and replay cached replies.

## Main Contents

- Cache size bounds:
  - `NFSRVCACHE_MAX_SIZE` is 2048.
  - `NFSRVCACHE_MIN_SIZE` is 64.
- `struct nfsrvcache` stores:
  - LRU and hash links,
  - RPC XID,
  - cached reply mbuf or cached reply status,
  - client host address,
  - RPC procedure number,
  - request state,
  - flag bits.
- Accessor macros alias reply/status and address union fields.
- Request states:
  - `RC_UNUSED`,
  - `RC_INPROG`,
  - `RC_DONE`.
- Cache lookup return decisions:
  - `RC_DROPIT`,
  - `RC_REPLY`,
  - `RC_DOIT`,
  - `RC_CHECKIT`.
- Flags track locking/waiting, reply representation, NQNFS, and address representation.

## Notable Details

- Cached replies may be stored either as an mbuf chain or as a status code.
- Address storage supports compact IPv4 address or full sockaddr-like name via `union nethostaddr`.
- Return values directly drive the server loop in `nfssvc_nfsd()`.

## Integration

Used by server duplicate-request cache implementation in `nfs_srvcache.c` and by `nfs_syscalls.c` when deciding whether to execute, reply from cache, or drop an incoming RPC.
