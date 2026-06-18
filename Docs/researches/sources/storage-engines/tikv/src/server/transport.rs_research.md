# sources/storage-engines/tikv/src/server/transport.rs

## Purpose

This module adapts TiKV's `RaftClient` to raftstore's `Transport` trait so raftstore can send raft messages without depending directly on the server raft client implementation.

## Important APIs, Types, And Functions

`ServerTransport<T, S>` wraps `RaftClient<S, T>`, where `T: RaftExtension` and `S: StoreAddrResolver`. `new` constructs the wrapper, `Clone` delegates to the underlying client clone, and the `Transport` implementation exposes `send`, `set_store_allowlist`, `need_flush`, and `flush`.

## Control Flow

`send` forwards a `RaftMessage` to `raft_client.send`. Success is returned unchanged; failure reason is wrapped as `raftstore::Error::Transport`. Allowlist and flushing methods are direct pass-throughs.

## State And Persistence Behavior

The wrapper owns no persistent state beyond the cloned raft client. Any batching, connection state, allowlist state, or pending messages live in `RaftClient`.

## Dependencies And Integration Points

This is the integration boundary between `crate::server::raft_client`, store address resolution, `tikv_kv::RaftExtension`, and raftstore's transport abstraction.

## Risks And Edge Cases

The module intentionally hides raft-client-specific errors behind raftstore transport errors, so downstream code receives less structured detail. Flush semantics depend entirely on `RaftClient::need_flush` and `flush`; this adapter adds no additional synchronization.

## Test Signals

No local tests are present. Coverage is expected through raftstore/server integration tests that exercise raft message delivery, allowlists, and flush behavior.
