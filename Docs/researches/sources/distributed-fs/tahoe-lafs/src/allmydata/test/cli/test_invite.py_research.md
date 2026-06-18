# sources/distributed-fs/tahoe-lafs/src/allmydata/test/cli/test_invite.py

## Purpose
This module tests `tahoe invite` and `create-client --join` invitation flows over a controlled in-memory magic-wormhole implementation. It validates successful invite generation, join-side config creation, share-parameter propagation, introducer FURL handling, and protocol ability negotiation failures.

## Important APIs, Types, and Functions
- `open_wormhole` creates a `MemoryWormholeServer`, injects it into `runner.Options`, creates one wormhole endpoint, and returns a `run_cli` partial, wormhole, and code.
- `make_simple_peer` returns an async peer function that waits for the invite wormhole, mirrors its code, and sends preselected JSON messages.
- `send_messages` serializes JSON-like values with `dumps_bytes` and sends them over a wormhole.
- `concurrently` runs client and server coroutine/generator functions through `defer.gatherResults`.
- `Join` tests consuming an invitation during `create-client --join`.
- `Invite._invite_success` factors successful server-side invite tests.

## Control Flow
Join tests create one end of a wormhole, send server abilities and invite payloads, run `create-client --join <code>`, and inspect the resulting client config. Invite tests create an introducer directory, write `private/introducer.furl` when needed, run the server-side `invite` command with injected wormhole options, and concurrently run a simple peer that sends client abilities. After success, the peer reads two server messages: abilities followed by the invitation.

## State and Persistence Behavior
Tests create introducer and client node directories. `private/introducer.furl` is manually written because the introducer is not started. `tahoe.cfg` may be overwritten with specific share settings, then read back through `read_config` or direct file reads. Joined clients persist nickname, introducer FURL, and share settings into their config. Wormhole state lives only in memory and is isolated per test.

## Dependencies and Integration Points
The module depends on Twisted Deferreds, `runner.Options`, `run_cli`, `GridTestMixin`, `CLITestMixin`, `read_config`, Tahoe JSON byte helpers, and `.wormholetesting`. It is the integration point between CLI creation, introducer configuration, invitation protocol JSON, and magic-wormhole transport abstraction.

## Risks and Edge Cases
Covered risks include unknown invite payload keys, missing introducer FURL, missing nickname argument, wrong or missing client abilities, wrong or missing server abilities, and share configuration defaults. The tests ensure unsupported protocol versions fail with clear messages while harmless unknown invite fields are ignored on join.

## Test Signals
The tests exercise both protocol directions and parse real JSON messages exchanged over the fake wormhole. They also verify persisted client config after join. A limitation is that real network wormhole behavior is intentionally replaced by the in-memory helper.
