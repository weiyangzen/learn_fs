# sources/storage-engines/tikv/components/pd_client/src/meta_storage.rs

Purpose: Defines the PD meta-storage client abstraction, a trimmed etcd-like key/value API used by TiKV callers that need generic metadata storage through PD. It wraps protobuf requests from `kvproto::meta_storagepb` and exposes a typed trait so callers can compose decorators such as source tagging and response checking.

Important APIs/types/functions: `Get`, `Put`, `Watch`, and `Delete` are builder-style request wrappers. `Get::of`, `prefixed`, `range_to`, `rev`, and `limit` control exact, prefix, range, revision, and limit scans. `Put::fetch_prev_kv` requests prior data. `Watch::from_rev` and `with_prev_kv` configure streaming watches. `Source` names known callers (`LogBackup`, `ResourceControl`, `RegionLabel`). `Sourced<S>` injects the caller string into every request header. `Checked<S>` and `CheckedStream<S>` convert response-header errors into `crate::Error`. `MetaStorageClient` is the core async trait with `get`, `put`, `delete`, and streaming `watch`; an `Arc<S>` forwarding impl makes shared clients usable directly.

Control flow: Request builders mutate protobuf inner messages. `Sourced` wraps each trait call, mutates the request header, then forwards to the inner client. `Checked` maps each future or stream event through `check_resp_header`, returning `DataCompacted` distinctly from unknown metadata errors.

State and persistence behavior: This file itself stores no local state beyond wrapper fields. Persistence is remote, in PD meta storage. The `INF = [0]` sentinel and `codec::next_prefix_of` encode etcd-compatible infinity ranges for full-prefix requests.

Dependencies and integration points: It depends on `futures::Stream`, `kvproto::meta_storagepb`, `tikv_util::codec`, and crate-level `PdFuture`, `Result`, and `Error`. It is constructed from the PD client channel in `pd_client::util::Client` and is consumed by higher-level TiKV services that need PD-backed metadata.

Risks: Prefix range handling relies on `[0]` matching etcd's infinity convention; misuse could create too-wide or too-narrow watches. `CheckedStream` uses an unsafe pin projection, although the projection is trivial. `Source` is a closed enum, so new metadata callers must add a variant or lose source attribution. `GlobalConfigNotFound`-style PD errors are not represented here, only meta-storage error kinds.

Test signals: No tests are local to this file. Coverage is expected through PD client integration tests and consumers that exercise meta-storage `get/put/delete/watch`, especially `DataCompacted` watch behavior and prefixed range requests.
