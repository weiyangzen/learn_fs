# sources/storage-engines/tikv/components/test_pd/src/mocker/etcd.rs

## Purpose
This file implements a small in-memory, revisioned etcd-like key-value store used by the PD MetaStorage mock. It supports range/key/prefix reads, puts, deletes with tombstones, and watch streams.

## Important APIs, Types, And Functions
`Etcd` stores versioned `items` in a `BTreeMap<Key, Value>`, active subscribers, current revision, and a subscriber ID allocator. `get_key` returns the latest non-deleted value per logical key in a requested range plus the current revision. `set` allocates a new revision, notifies matching subscribers with `KvEventType::Put`, and stores a `Value::Val`. `delete` tombstones matching keys and notifies subscribers with `Delete` events carrying previous data. `watch` sends historical events from `start_rev` and registers a live mpsc subscriber.

`MetaKey` provides `next` and `next_prefix` range-bound helpers. `KeyValue`, `KvEventType`, `KvEvent`, and `Keys` are the public data wrappers used by `meta_storage.rs`.

## Control Flow And State
Every mutation increments `revision`. The backing map stores `(key, revision)` entries, so historical events remain available for watch startup. Reads chunk by logical key and choose the last revision in range, filtering tombstones. Watches use bounded Tokio mpsc channels and are retained in `subs` until `clear_subs` or store drop.

## Persistence And Integration Points
There is no disk persistence; this is process-local test state. It integrates with `MetaStorage` through an `Arc<Mutex<Etcd>>` client and returns `ReceiverStream<KvEvent>` for gRPC streaming.

## Risks And Test Signals
The store is a simplified etcd model: no compaction, transactions, leases, compare-and-swap, or subscriber removal on stream close. `set`/`delete` unwrap subscriber sends, so dropped receivers can panic. Prefix end calculation for all-`0xff` keys can shrink to an empty bound, so tests should stay in normal metadata key domains.
