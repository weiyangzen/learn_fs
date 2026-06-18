# sources/storage-engines/tikv/components/test_pd/src/mocker/meta_storage.rs

## Purpose
This mocker implements PD MetaStorage RPCs over the in-memory `Etcd` emulator. It lets tests exercise metadata get/put/delete/watch behavior without a real etcd.

## Important APIs And Functions
`MetaStorage` owns `Arc<Mutex<Etcd>>`. `check_header` requires `RequestHeader.source` to be non-empty and returns an error otherwise. `meta_store_get` maps key/range requests to `Keys`, reads items and revision, and returns protobuf `KeyValue`s with a revision header. `meta_store_put` stores a key/value pair. `meta_store_delete` deletes a single key. `meta_store_watch` validates the header, opens an etcd watcher from the requested revision, and spawns a gRPC streaming task that converts put/delete events into `mpb::WatchResponse`s.

## Control Flow And State
Unary calls lock the backing store and use `block_on` for async etcd operations. Watch calls create a receiver stream and then release control to a spawned async loop that sends responses until the watcher ends. Delete events include `prev_kv` as well as event key/value.

## Persistence And Integration Points
Persistence is in-memory only through `Etcd`. The mocker integrates with the `meta_storagepb` gRPC service implementation in `server.rs` and grpcio streaming sinks.

## Risks And Test Signals
Invalid headers are surfaced as either trait errors for unary calls or `INVALID_ARGUMENT` stream failure for watch calls. The store lock is a standard mutex while etcd methods are async and then blocked on; this is acceptable for tests but not a production pattern. Watch send unwraps can panic if the client disconnects unexpectedly.
