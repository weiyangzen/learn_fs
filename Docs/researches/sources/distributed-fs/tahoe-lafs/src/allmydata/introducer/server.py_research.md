## sources/distributed-fs/tahoe-lafs/src/allmydata/introducer/server.py

### Purpose
This module builds and runs the Tahoe introducer node and implements the server-side v2 publish/subscribe service. The introducer remembers the latest signed announcement for each `(service_name, signing_key)` pair and forwards matching announcements to subscribers.

### Important APIs, Types, and Functions
`create_introducer` reads/creates node configuration, builds I2P/Tor providers and the main Foolscap tub, and returns a `_IntroducerNode` in a Deferred-like success or a Twisted `Failure` on exception. `_IntroducerNode` subclasses `node.Node`, initializes the introducer service, registers it with the tub, migrates old public `introducer.furl` files to `private/introducer.furl`, and optionally starts web status. `FurlFileConflictError` protects conflicting old/new FURL files. `stringify_remote_address` normalizes subscriber peer addresses. `IntroducerService` implements `RIIntroducerPublisherAndSubscriberService_v2` and exposes `remote_get_version`, `remote_publish_v2`, `remote_subscribe_v2`, `get_announcements`, and `get_subscribers`.

### Control Flow
Node creation builds transport providers and tub options from config, then `_IntroducerNode.init_introducer` validates that the tub is listening before registering `IntroducerService`. Publication calls enter `remote_publish_v2`, then `publish`, then `_publish`. `_publish` verifies the signed tuple with `unsign_from_foolscap`, extracts `service-name`, and compares it with the old announcement for the same index. Exact duplicates are ignored. Sequenced updates must provide a newer integer `seqnum`; stale or unsequenced replacements are rejected. Accepted announcements are stored and pushed via subscriber `announce_v2` calls to all subscribers for that service.

Subscription calls enter `remote_subscribe_v2`, normalize bytes/text keys into `UnicodeKeyDict`, and call `add_subscriber`. `add_subscriber` records the remote subscriber, registers a disconnect cleanup callback, and immediately sends any already-known announcements for that service.

### State and Persistence Behavior
Server memory state includes `_announcements`, keyed by `(service_name, key_s)` and containing `(ann_t, canary, ann, timestamp)`, plus `_subscribers`, keyed by service name and then subscriber remote reference. Debug counters track inbound messages, duplicates, replay failures, updates, outbound messages, and subscriptions. Persistent state is the registered private `introducer.furl`; old public FURL migration is intentionally guarded.

### Dependencies and Integration Points
The module integrates Twisted services/deferreds/failures, Foolscap `Referenceable`, Tahoe node configuration and tub helpers, I2P/Tor provider creation, Tahoe logging, `dictutil.UnicodeKeyDict`, and `introducer.common`. Web status integrates through `IntroducerWebishServer`.

### Risks and Edge Cases
`create_introducer` returns `Failure()` instead of raising, so callers must handle both success and failure Deferred values. `FurlFileConflictError` intentionally stops ambiguous FURL migration. Replay protection only applies when the old announcement had `seqnum`; first announcements without sequence numbers can be accepted. Subscriber remote failures are logged asynchronously. The canary is stored for status but disconnect pruning of announcements is not active.

### Test Signals
`test_introducer.py` covers service construction, publish/subscribe behavior, duplicate and stale announcement rejection, v2 version advertisement, FURL conflict handling, subscriber status, and signature paths. Web introducer tests exercise status display data produced from descriptors.
