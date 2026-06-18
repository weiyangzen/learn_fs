# sources/distributed-fs/tahoe-lafs/src/allmydata/test/test_introducer.py

## Purpose
Tests introducer node creation, client/server announcement handling, signed announcement semantics, duplicate/replay protection, reconnect behavior, persisted client caches, unsupported-version failures, FURL decoding, and signature validation.

## APIs / Types / Functions
- `Node`, `Introducer`, `Client`, `Server`, `Queue`, `SystemTest`, `ClientInfo`, `Announcements`, `ClientSeqnums`, `NonV1Server`, `DecodeFurl`, and `Signatures` cover distinct introducer surfaces.
- `ServiceMixin` manages a Twisted `MultiService` parent and eventual queue flushing.
- `fakeseq`, `realseq`, `make_ann`, and `make_ann_t` build signed Foolscap announcement tuples.
- `TooNewServer` simulates an unsupported future protocol.

## Control Flow
Creation tests cover config directory creation, legacy/public versus private `introducer.furl` migration/conflict behavior, unreadable `introducers.yaml`, and web static path resolution. Client/server tests publish signed announcements with duplicate, old, missing, invalid, and newer sequence numbers to verify deduplication and replacement. System tests create one introducer and six clients, publish storage announcements from five clients, assert debug counters and web rendering, then exercise Tub and service restarts. Cache tests write/read `private/introducer_default_cache.yaml` and load announcements into a new client.

## State And Persistence
Exercises node basedirs, `private/introducer.furl`, legacy `introducer.furl`, `tahoe.cfg`, `private/introducers.yaml`, `private/introducer_default_cache.yaml`, and `announcement-seqnum`. Runtime state includes announcement tables, subscribers, debug counters, outstanding queues, reconnectors, and Tub registrations.

## Dependencies / Integration Points
Integrates Twisted services, Foolscap Tubs, Ed25519 signing, Tahoe introducer client/server/common modules, client creation, YAML utilities, web introducer status rendering, and polling/eventual-queue helpers.

## Risks And Test Signals
Tests rely on private debug counters and event settling, so reconnect paths can be timing-sensitive. `ClientSeqnums` is marked broken, indicating known sequence-number persistence risk. Passing tests signal signed v2 announcements are replay-protected, cached, delivered, rendered, and re-published correctly across reconnects/restarts.
