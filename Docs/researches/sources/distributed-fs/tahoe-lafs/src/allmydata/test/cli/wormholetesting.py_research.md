# sources/distributed-fs/tahoe-lafs/src/allmydata/test/cli/wormholetesting.py

## Purpose
This file provides an in-memory implementation of the subset of magic-wormhole interfaces used by Tahoe-LAFS tests. It lets invite/join tests exercise wormhole protocol behavior without a real relay server or network.

## Important APIs, Types, and Functions
- Public `__all__`: `MemoryWormholeServer`, `TestingHelper`, `memory_server`, and `IWormhole`.
- `MemoryWormholeServer.create` mimics `wormhole.wormhole.create`, validates unsupported Tor/dilation options, creates `_MemoryWormhole` instances, and notifies app waiters.
- `TestingHelper.wait_for_wormhole` waits for a wormhole for a given appid/relay URL pair.
- `_verify` compares the fake `create` signature against the real wormhole `create` function enough to detect incompatible API drift.
- `_WormholeApp` stores wormholes by code, generates deterministic test codes, and manages waiters for peers.
- `_WormholeServerView` scopes app state by `(relay_url, appid)` and finds peer wormholes by code.
- `_MemoryWormhole` implements `IWormhole` methods used by tests: code allocation, `set_code`, `when_code`, `get_welcome`, `send_message`, `when_received`, aliases `get_message`/`get`, and `close`.
- `memory_server` returns a server plus helper pair.

## Control Flow
Tests call `MemoryWormholeServer.create` to create endpoint A. `get_code` lazily allocates a code through `_WormholeApp.allocate_code`. A second endpoint calls `set_code`, which registers it under the same code. `send_message` enqueues payload bytes on the sending endpoint's `DeferredQueue`. `when_received` locates the opposite endpoint under the same code and returns a Deferred for its queued payload. Helper waiters allow tests to wait until a command under test has created its wormhole before creating the peer endpoint.

## State and Persistence Behavior
All state is in memory. `MemoryWormholeServer._apps` maps `(relay_url, appid)` to `_WormholeApp`. `_WormholeApp.wormholes` maps codes to endpoint lists, `_waiting` stores Deferreds for future endpoints, and `_counter` generates deterministic codes. `_MemoryWormhole` stores its code, outgoing payload queue, and Deferreds waiting for code assignment. There is no persistence, cleanup, or network I/O.

## Dependencies and Integration Points
The helper depends on `attrs`, Twisted `Deferred`, `DeferredQueue`, `succeed`, `wormhole._interfaces.IWormhole`, the real `wormhole.wormhole.create` for signature comparison, and `zope.interface.implementer`. It is used by `test_invite.py` through `MemoryWormholeServer`, `TestingHelper`, and `memory_server`.

## Risks and Edge Cases
Risks include drift from real magic-wormhole APIs, unsupported Tor/dilation paths, multiple waiters for the same app key, code reuse, trying to receive before code assignment, and peer lookup when the other endpoint is absent. The implementation is intentionally incomplete and deterministic; it is not suitable outside tests.

## Test Signals
The `_verify` call runs at import time and catches broad signature incompatibility. Invite tests provide behavioral coverage of the message-passing paths. The helper itself does not have a standalone test suite in this subset, so behavior is mostly exercised indirectly.
