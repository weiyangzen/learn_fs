# sources/storage-engines/tikv/tests/integrations/server/security.rs

## Purpose
This file verifies TiKV server-side TLS common-name filtering for gRPC clients. It starts a one-node server cluster with generated test security credentials and checks that a client certificate whose CN is allowed can issue a `kv_get`, while an unapproved CN is rejected.

## Important APIs, Types, and Functions
The tests use `new_server_cluster`, `test_util::new_security_cfg`, `test_util::new_channel_cred`, `grpcio::ChannelBuilder::secure_connect`, and `kvproto::tikvpb::TikvClient`. `HashSet<String>` configures allowed CNs on `cluster.cfg.security`.

## Control Flow
Each test creates a cluster, sets `security` config, runs the cluster, finds the leader store address from the simulator registry, constructs a secure gRPC channel, and calls `TikvClient::kv_get`. The success case unwraps the response; the failure case asserts the RPC returns an error.

## State, Persistence, and Dependencies
State is limited to the temporary server cluster and in-memory security configuration. It depends on test certificates matching the expected `"tikv-server"` CN and on the test raftstore simulator exposing store addresses.

## Integration Points, Risks, and Test Signals
The integration point is the full gRPC server credential path rather than a unit-level security manager call. Test signal is binary RPC success/failure. The failure case uses the misspelled string `"invaild-server"`, which is harmless but should not be copied into documentation as a canonical name.
