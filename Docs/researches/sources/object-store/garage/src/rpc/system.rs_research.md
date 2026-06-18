# sources/object-store/garage/src/rpc/system.rs

Purpose: cluster membership manager. It owns node identity, NetApp RPC listener, full-mesh peering, discovery, status exchange, layout manager, health reporting, and system RPC handling.

Important APIs and types: `SystemRpc` includes connect, status, known-node, and layout pull/advertisement messages. `System` stores local ID, persisted peer list, local/remote statuses, NetApp, peering manager, endpoint, listen/public addresses, optional discovery configs, layout manager, metrics, replication factor, and data/metadata paths. Functions include `read_node_id`, `gen_node_key`, `System::new`, `run`, `get_known_nodes`, `connect`, `health`, discovery/status loops, and `EndpointHandler<SystemRpc>`.

Control flow: startup reads or generates an ed25519 node key, creates `NetApp`, endpoint, peering manager, peer-list persister, layout manager, local status, optional discovery clients, and metrics. `run` joins listener, peering, discovery, and status loops. Discovery resolves bootstrap peers, reloads persisted peers, optionally queries Consul/Kubernetes, filters to layout nodes when appropriate, tries connections asynchronously, saves peers, and advertises itself. Status exchange broadcasts local status every 10 seconds. RPC handling delegates layout messages to `LayoutManager`.

State and persistence: persists `node_key`, `node_key.pub`, and `peer_list`; layout persistence is delegated. Local and remote node statuses are in `RwLock`s.

Dependencies and integration: integrates config, NetApp, peering, discovery modules, layout, RPC helper, metrics, disk usage, and node health.

Risks and test signals: replication-factor mismatch can terminate the process for safety. Public address autodetection can be wrong on complex networks. Discovery loops spawn connection attempts without awaiting them. Health depends on current layout validity. Tests are mostly external/integration.
