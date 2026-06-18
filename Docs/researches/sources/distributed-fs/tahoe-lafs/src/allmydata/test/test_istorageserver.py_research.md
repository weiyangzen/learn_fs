# sources/distributed-fs/tahoe-lafs/src/allmydata/test/test_istorageserver.py

## Purpose
Protocol-contract suite for `IStorageServer`, the storage client interface. Shared mixins are applied to both Foolscap and HTTP storage clients to ensure protocol migration preserves immutable and mutable storage semantics.

## APIs / Types / Functions
- `new_storage_index`, `new_secret`, and `_randbytes` produce deterministic test inputs.
- `IStorageServerSharedAPIsTestsMixin` checks `get_version`.
- `IStorageServerImmutableAPIsTestsMixin` covers bucket allocation, write/read, abort/disconnect cleanup, corrupt-share advice, and immutable leases.
- `IStorageServerMutableAPIsTestsMixin` covers STARAW, `slot_readv`, mutable corrupt-share advice, and mutable leases.
- `_SharedMixin` builds a system node, locates `StorageServer`, installs a fake clock, and obtains an `IStorageServer` client.

## Control Flow
Immutable tests allocate buckets, repeat allocations, write fully/partially, read completed buckets, validate overlapping writes, abort/disconnect and rewrite, read out of bounds, advise corrupt shares, and assert lease create/renew/add behavior. Mutable tests validate atomic read/test/write semantics, pre-write read ordering, tests past end, write-enabler failures, zero-length delete, slot reads, and mutable leases. Protocol-specific classes run the same mixins with `FORCE_FOOLSCAP_FOR_STORAGE` true or false.

## State And Persistence
Creates real Tahoe client/server services and storage state. Share data, mutable slots, and leases live in the backing `StorageServer`. Lease timing uses a deterministic Twisted `Clock`.

## Dependencies / Integration Points
Ties together `IStorageServer`, `StorageServer`, Foolscap remote bucket objects, HTTP storage clients, `SystemTestMixin`, Deferreds, and lease bookkeeping.

## Risks And Test Signals
Adapters must preserve Foolscap-like `callRemote` bucket surfaces. Expected protocol failures are asserted as `RemoteException`. Passing tests demonstrate equivalent Foolscap/HTTP semantics for storage versioning, immutable operations, mutable STARAW/readv, and lease behavior.
