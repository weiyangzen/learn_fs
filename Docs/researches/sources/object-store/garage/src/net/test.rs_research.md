# sources/object-store/garage/src/net/test.rs

Purpose: integration tests for the Garage NetApp peering layer under single-threaded and multi-threaded Tokio schedulers.

Important APIs and functions: `test_with_basic_scheduler` and `test_with_threaded_scheduler` are ignored `tokio::test`s that call `run_test`. `run_test` wraps `run_test_inner` in a 20 second timeout. `run_test_inner` creates three keypairs, three loopback addresses, starts three NetApps with a shared network key, and asserts peer-list convergence. `run_netapp` constructs `NetApp`, `PeeringManager`, and a spawned task running `listen` and `peering.run`.

Control flow: node 1 starts alone, node 2 bootstraps from node 1, the tests wait for gossip/peering convergence, and both peer managers should report two peers. Node 3 then bootstraps from node 2, waits again, and all three peer managers should report three peers. A watch channel broadcasts shutdown and the spawned tasks are awaited.

State and persistence: no persistent state. Runtime state consists of generated sodiumoxide auth/signing keys, socket listeners, peering state, and the stop watch channel.

Dependencies and integration: covers `NetApp::new`, `NetApp::listen`, `PeeringManager::new`, `PeeringManager::run`, `get_peer_list`, network handshakes, and connection propagation. It uses loopback TCP ports based at `19980` and `19990`.

Risks and test signals: both tests are marked `#[ignore = "flaky"]`, which is itself a strong signal that timing and port reuse are fragile. The fixed sleeps make tests scheduler/load dependent. They are still valuable as manual smoke tests for authenticated peering and shutdown behavior.
