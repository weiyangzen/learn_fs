## sources/distributed-fs/tahoe-lafs/src/allmydata/introducer/client.py

### Purpose
`IntroducerClient` is the client-side Foolscap service used by Tahoe nodes to publish local services and subscribe to peer service announcements. It signs outbound announcements, verifies inbound signed announcements, filters them by service, persists a YAML cache for startup/offline use, and reports connection status to the introducer.

### Important APIs, Types, and Functions
`InvalidCacheError` marks malformed cache input. `V2` is the required introducer protocol key. `IntroducerClient` implements `RIIntroducerSubscriberClient_v2` and `IIntroducerClient`. Its public methods are `startService`, `subscribe_to`, `publish`, `remote_announce_v2`, `got_announcements`, `connection_status`, `connected_to_introducer`, and `get_since`. Internal helpers include `_load_announcements`, `_save_announcements`, `_got_introducer`, `_got_versioned_introducer`, `_maybe_subscribe`, `_maybe_publish`, `create_announcement_dict`, `_process_announcement`, and `_deliver_announcements`.

### Control Flow
On `startService`, the client starts a Foolscap reconnection to the introducer and separately attempts `getReference`; initial connection failure loads cached announcements so local subscribers can still see remembered peers. Once connected, `_got_introducer` obtains remote version information and `_got_versioned_introducer` requires v2, records the publisher reference, registers disconnect handling, then publishes/subscribes any queued state.

`subscribe_to` registers a local callback in an `ObserverList`, sends a remote `subscribe_v2` if connected, and immediately replays cached inbound announcements for the requested service. `publish` obtains a monotonic sequence/nonce from the caller-provided sequencer, builds service announcement dictionaries, signs every outbound announcement with `sign_to_foolscap`, and republishes all signed announcements. Inbound `announce_v2` calls are passed through `got_announcements`; each announcement is unsigned and signature-verified, then `_process_announcement` rejects wrong services, exact duplicates, and stale/replayed sequence numbers before saving and delivering the new state.

### State and Persistence Behavior
Important in-memory state includes `_outbound_announcements` before signing, `_published_announcements` after signing, `_publisher`, `_subscriptions`, `_local_subscribers`, `_inbound_announcements`, `_since`, and debug counters. `_inbound_announcements` is keyed by `(service_name, key_s)` and stores `(announcement, verifying_key, timestamp)`. `_save_announcements` persists inbound state to `cache_filepath` as YAML entries containing `ann` and ASCII `key_s`; `_load_announcements` tolerates a missing cache but logs malformed shapes.

### Dependencies and Integration Points
The client integrates Twisted `service.Service`, Foolscap `Referenceable`, Tahoe `log`, YAML helpers, connection status conversion, remote-reference version negotiation, Ed25519 signature helpers from `introducer.common`, and crypto `BadSignature`. `allmydata.client` constructs introducer clients; `storage_client.py` subscribes to storage announcements; tests use `MemoryIntroducerClient` for model-only behavior.

### Risks and Edge Cases
Replay protection depends on valid integer `seqnum`; announcements without valid newer sequence numbers cannot replace an existing sequenced announcement. Cache loading assumes keys like `key_s` and `ann` are present in dict entries; malformed entries are logged but individual missing keys could still surface if not shaped as expected. Python bytes/text normalization is explicit but fragile around `service-name`, `nickname`, and YAML encodings. Signature failures are ignored per-announcement, so mixed batches continue processing. `_subscriptions` is cleared on disconnect so resubscribe happens on reconnect.

### Test Signals
`test_introducer.py` covers client instantiation, v2 version requirements, cache behavior, bad signatures, duplicate/replay/update behavior, publish/subscribe flows, and connection failure handling. Web and storage-client tests exercise `connected_to_introducer` and service announcement consumption. The signature tests verify invalid signatures are not delivered to subscribers.
