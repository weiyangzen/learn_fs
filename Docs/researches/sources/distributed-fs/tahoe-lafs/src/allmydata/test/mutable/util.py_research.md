# sources/distributed-fs/tahoe-lafs/src/allmydata/test/mutable/util.py

## Purpose
This file provides the in-memory mutable-file test harness used by the mutable test suite. It replaces real storage servers with local fake Foolscap-like objects and gives tests tools to publish files, create competing versions, reorder or delay reads, and corrupt shares by logical layout offsets.

## Important APIs, Types, And Functions
Core classes are `FakeStorage`, `FakeStorageServer`, `Peer`, `PublishMixin`, and `CheckerMixin`. Utility functions include `eventuaaaaaly`, `flip_bit`, `add_two`, `corrupt`, `make_peer`, `make_storagebroker`, `make_storagebroker_with_peers`, `make_nodemaker`, `make_nodemaker_with_peers`, and `make_nodemaker_with_storage_broker`. It uses `StorageFarmBroker`, `NodeMaker`, `SecretHolder`, `KeyGenerator`, `MutableData`, `MDMFSlotReadProxy`, `SDMF_VERSION`, and `MDMF_VERSION`.

## Control Flow
`FakeStorageServer.callRemote` wraps local method invocation in `fireEventually`, making fake storage asynchronous enough for Deferred-based code. Reads can be delayed and released in a configured peer order. Writes patch share bytes in a `BytesIO`. `corrupt` parses each share's version information, resolves symbolic offsets such as `signature` or `share_data`, flips a bit, and returns a `DeferredList`.

## State, Persistence, And Dependencies
All shares live in `FakeStorage._peers`, keyed by peer id and share number. `PublishMixin` resets fake storage for each publish helper and stores nodes as `self._fn` and `self._fn2`; `publish_multiple` snapshots share dictionaries into `self._copied_shares` so tests can mix historical versions. There is no disk persistence.

## Risks And Test Signals
The helpers intentionally implement only the subset of RIStorageServer behavior the tests need. That makes tests fast and controllable, but it can hide failures tied to real server semantics such as test-vector enforcement, leases, or transport serialization. Since many mutable tests depend on exact `k=3,n=10` defaults and share layout offsets, changes here can ripple widely.
