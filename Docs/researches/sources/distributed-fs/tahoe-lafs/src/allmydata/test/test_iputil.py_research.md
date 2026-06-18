# sources/distributed-fs/tahoe-lafs/src/allmydata/test/test_iputil.py

## Purpose
Tests networking utilities for unused Foolscap Tub listen ports, descriptor-related GC tracking, and synchronous local IPv4 address discovery.

## APIs / Types / Functions
- `retry` and `stop_after_attempt` provide bounded retry around race-prone port tests.
- `ListenOnUsed` covers `iputil.listenOnUnused`.
- `GcUtil` covers `gcutil._ResourceTracker`.
- `GetLocalAddressesSyncTests` covers `get_local_addresses_sync`.

## Control Flow
The random-port test starts a Tub, listens on an unused port, connects via a socket, and verifies a second Tub gets a different port. The specific-port test discovers a free port and checks Tahoe uses it. GC tests patch `gc.collect` and count calls after allocation/release patterns. Address tests assert returned values are native strings parseable as IPv4 addresses.

## State And Persistence
Creates Tub cert files and local sockets. Resource tracker state is in-memory. No durable Tahoe config is written.

## Dependencies / Integration Points
Integrates Foolscap Tub listening, Python sockets, Tahoe `iputil`/`gcutil`, Twisted cleanup, and testtools matchers.

## Risks And Test Signals
Port allocation remains inherently race-prone, which is why retry exists. Host networking differences can affect address discovery. Passing tests show Tahoe can allocate usable ports, throttle GC, and return parseable local IPv4 addresses.
