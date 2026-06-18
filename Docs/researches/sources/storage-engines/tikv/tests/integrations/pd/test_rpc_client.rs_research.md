# sources/storage-engines/tikv/tests/integrations/pd/test_rpc_client.rs

Purpose: validates `pd_client::RpcClientV2` behavior against mock PD servers: connection retry, endpoint validation, forwarding, metadata APIs, TSO streaming, region/store heartbeats, leader changes, reconnect notifications, cluster version feature gates, and error mapping.

Important APIs and functions: `setup_runtime` creates a one-thread Tokio runtime for stream tests. `must_get_tso` uses `create_tso_stream` with `WakePolicy::Immediately`. Tests construct `MockServer` with mockers such as `Split`, `AlreadyBootstrapped`, `Incompatible`, and `LeaderChange`; instantiate clients with `new_client_v2`; and use `PdConnector::validate_endpoints`, `RpcClientV2::new`, `subscribe_reconnect`, `feature_gate`, `store_heartbeat`, `create_region_heartbeat_stream`, and region/store query methods.

Control flow: tests bind mock PD endpoints, create a v2 client, perform synchronous metadata calls or async stream operations under the runtime, then mutate mock server state or failpoints to force reconnect paths. Leader-change scenarios repeatedly issue harmless region queries until the client notices a new leader, then assert reconnect broadcasts and heartbeat stream recovery.

State and persistence: state lives in mock PD handlers: allocated IDs, stores, regions, tombstone store entries, leader member records, cluster version strings, and stream response queues. Client-side state includes cached cluster id, leader endpoint, feature gate version, reconnect broadcast channel, and heartbeat/TSO streams.

Dependencies and integration points: integrates `grpcio`, `kvproto::pdpb/metapb`, `pd_client::{PdClientV2, PdConnector, RpcClientV2}`, `security::SecurityManager`, `test_pd` mock server/mocker utilities, failpoints, Tokio, futures streams, and `txn_types::TimeStamp`.

Risks: stream tests are timing-sensitive and rely on fixed sleeps around default retry intervals. Error comparisons sometimes stringify gRPC errors. Failpoints such as `connect_leader`, `cluster_id_is_not_ready`, and `region_heartbeat_send_failed` must be removed. Mock behavior may not cover every production PD edge, especially with forwarding enabled.

Test signals: nonzero cluster id, monotonic ID allocation, correct tombstone filtering/error codes, expected `ClusterBootstrapped` and `Incompatible` errors, heartbeat responses after failures and leader changes, reconnect notifications, and monotonic feature-gate enabling as cluster versions advance but not regress.
