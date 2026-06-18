# sources/object-store/garage/src/net/peering.rs

## Purpose
This file implements the full-mesh peering strategy for `NetApp`. It tracks known peer addresses, manages outgoing reconnection attempts, sends pings, detects dead links, exchanges peer lists, prunes stale addresses, and publishes peer health information.

## Important APIs, types, and functions
Protocol messages are `PingMessage` and `PeerListMessage`. `KnownAddr` tracks address success/failure. `PeerInfoInternal` stores known addresses, connection state, last ping/seen times, recent ping durations, and failed ping count. Public `PeerInfo` reports state and ping stats. `PeerConnState` is `Ourself`, `Connected`, `Waiting`, `Trying`, or `Abandoned`. `PeeringManager::new`, `run`, `get_peer_list`, `set_ping_timeout_millis`, `ping`, `exchange_peers`, `handle_peer_list`, `try_connect`, `on_connected`, and `on_disconnected` drive the strategy. `pruning_sort_key` ranks addresses for removal.

## Control flow
Construction seeds known hosts with bootstrap peers and our own address, registers ping/peer-list endpoints, and installs NetApp connection callbacks. The run loop every second schedules pings for connected peers and retries for waiting peers. Pings use high priority and a configurable timeout; repeated failures beyond threshold disconnect the peer. Ping hash mismatch triggers peer-list exchange. Retry attempts sort addresses by recent success, shuffle never-successful addresses, try each address with NetApp, update success/failure counters, then prune to at most five addresses.

## State and persistence behavior
Peering state is in-memory only. `public_peer_list` is an `ArcSwap` snapshot for readers. Known-host hash is a sodiumoxide digest of the set of currently up node IDs, not addresses.

## Dependencies and integration points
It depends on `NetApp`, endpoints, message priorities, tokio, sodiumoxide hash, `arc-swap`, and random address shuffling. Garage system membership can query `get_peer_list` for status and use callbacks to keep full mesh connectivity.

## Risks and edge cases
Peer discovery is address gossip, not authenticated membership by itself; the NetApp handshake authenticates node IDs. Address pruning relies on consecutive failures and last success; NAT or changing public addresses can produce churn. Incoming disconnections do not change outgoing state. Failed pings disconnect after `FAILED_PING_THRESHOLD` but actual reconnect timing depends on callback state transitions. `run` sleeps with `tokio::time::sleep` and checks `must_exit.borrow()` only at loop top, so shutdown can wait up to loop delay.

## Test signals
`test_pruning_sort_key` covers stale address pruning priority. Additional tests should cover bootstrap initialization, hash changes, peer exchange, retry state transitions, ping failure disconnects, incoming/outgoing callback behavior, and public peer list stats.
