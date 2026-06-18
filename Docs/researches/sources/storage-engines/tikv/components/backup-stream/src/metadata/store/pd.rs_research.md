# sources/storage-engines/tikv/components/backup-stream/src/metadata/store/pd.rs

## Purpose
`metadata/store/pd.rs` adapts PD meta storage to the generic `MetaStore` abstraction for backup stream metadata. It supports PD get, put, prefix watch, and revision discovery.

## Important APIs, types, and functions
- `PdStore<M>` wraps a PD meta storage client.
- `convert_kv` converts `meta_storagepb::KeyValue` into metadata `KeyValue`.
- `PdWatchStream<S>` flattens PD `WatchResponse` batches into individual `KvEvent`s and converts PD/header errors into backup stream `Error`s.
- `RevOnly` is a snapshot that carries only a revision; point reads are not supported through `Snapshot::get_extra`.
- `MetaStore for PdStore<PD>` implements `snapshot`, prefix `watch`, unsupported `txn`/`txn_cond`, `set` via PD put, and `get_latest` via PD get.

## Control flow
`snapshot` performs a prefixed get on the metadata root with limit 0 to obtain a revision because point queries do not return one as needed. `watch` only accepts `Keys::Prefix`, constructs a PD watch from the requested start revision, wraps it in an abortable stream, and returns a cancel future. `get_latest` converts `Keys` into PD `Get` specs and maps the response key-values.

## State and persistence behavior
PD is the durable metadata backend. This adapter writes keys with `put` and reads current key state plus response revisions. It does not implement generic transaction APIs, so callers that require `txn` or `txn_cond` cannot use those paths against this adapter.

## Dependencies and integration points
Depends on `pd_client::meta_storage::{Get, Put, Watch, MetaStorageClient}`, `kvproto::meta_storagepb`, futures streams, and pin projection. Used by production metadata clients when backed by PD meta storage.

## Risks and edge cases
- `PdWatchStream::poll_next` asserts the internal buffer is empty before loading a new response; this matches the loop structure but assumes no reentrant buffer mutation.
- Watch supports prefixes only; exact-key/range watches return unsupported errors.
- `Snapshot::get_extra`, `txn`, and `txn_cond` are deliberately unsupported, creating an impedance mismatch with the full `MetaStore` trait.
- `get_latest` ignores the `more` flag because pagination is not implemented.

## Test signals
Tests use a mock PD meta storage server to verify exact and prefix query behavior, watch delivery/cancel behavior, source-check errors when the client lacks a log-backup source, and retry behavior under failpoints.
