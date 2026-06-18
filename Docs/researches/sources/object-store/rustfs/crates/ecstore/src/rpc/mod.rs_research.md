# sources/object-store/rustfs/crates/ecstore/src/rpc/mod.rs

Purpose: This file is the public module boundary for ecstore RPC support. It declares private RPC implementation modules and re-exports the types/functions that other ecstore components use for gRPC clients, HTTP auth, internode data transport, peer administration, peer S3 bucket operations, remote disk access, and remote locking.

Important APIs/types/functions: Private modules declared here are `client`, `context_propagation`, `http_auth`, `internode_data_transport`, `peer_rest_client`, `peer_s3_client`, `remote_disk`, and `remote_locker`. Re-exports include `TonicInterceptor`, signed/no-auth node-service client constructors, auth helpers and `TONIC_RPC_PREFIX`, `InternodeDataTransport` plus request/capability structs and builders, peer REST constants and `PeerRestClient`, `PeerS3Client`/`LocalPeerS3Client`/`RemotePeerS3Client`/`S3PeerSys`, `RemoteDisk`, and `RemoteClient`.

Control flow: There is no runtime control flow beyond Rust module initialization. Its compile-time role is to keep implementation modules private while exposing a curated API surface.

State and persistence behavior: The file owns no state and performs no persistence. Stateful behavior lives in the re-exported modules, notably connection caches, transport `OnceLock`, peer health trackers, and remote disk/locker implementations.

Dependencies and integration points: This is the integration point consumed by the rest of `ecstore`. It makes RPC internals available to storage pools, remote disks, admin/peer coordination, and bucket operations without requiring callers to know individual file paths. It also ensures auth and data-transport APIs are accessible to sibling modules through `crate::rpc`.

Risks: Because this module re-exports a broad set of internode primitives, API changes here can ripple through much of ecstore. `context_propagation` remains private, which is good for encapsulation but means new outbound transports must either use existing auth/client helpers or add new re-exports.

Test signals: No inline tests are present. Coverage comes indirectly from the re-exported modules' unit tests and any compile failures in downstream callers when the public RPC surface changes.
