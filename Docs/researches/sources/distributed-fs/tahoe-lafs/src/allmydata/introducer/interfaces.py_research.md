## sources/distributed-fs/tahoe-lafs/src/allmydata/introducer/interfaces.py

### Purpose
This module defines the v2 Foolscap introducer protocol and the local `IIntroducerClient` interface. It documents the signed announcement tuple format and the expected announcement/subscriber metadata used for Tahoe service discovery.

### Important APIs, Types, and Functions
`Announcement_v2` is currently `Any()` because signed announcement tuples are heterogeneous `(msg, sig_vs, claimed_key_vs)` values. `RIIntroducerSubscriberClient_v2` exposes remote `announce_v2(announcements)`. `RIIntroducerPublisherAndSubscriberService_v2` exposes remote `get_version`, `publish_v2`, and `subscribe_v2`. `SubscriberInfo` is a bytes-keyed Foolscap dictionary for diagnostic metadata. `IIntroducerClient` specifies `publish`, `subscribe_to`, and `connected_to_introducer`.

### Control Flow
The declared flow is publish/subscribe. Publishers call `publish_v2` with a signed announcement and canary. Subscribers call `subscribe_v2` with a remote subscriber reference and service name. The introducer calls subscriber `announce_v2` with matching announcements. Local consumers call `IIntroducerClient.subscribe_to`, which must invoke callbacks for new and changed announcements and tolerate duplicates.

### State and Persistence Behavior
No state is stored by this module, but it defines the state keys carried on the wire: announcement metadata such as `version`, `nickname`, `app-versions`, `my-version`, `oldest-supported`, `service-name`, storage FURLs, and plugin-specific fields. It also defines subscriber diagnostic metadata used by the server.

### Dependencies and Integration Points
It depends on Zope interfaces and Foolscap `RemoteInterface`, `Referenceable`, and constraints. `IntroducerClient` implements the subscriber remote interface and local interface; `IntroducerService` implements the publisher/subscriber service remote interface. `client.py`, `server.py`, storage discovery, and tests rely on the remote names being stable.

### Risks and Edge Cases
Remote interface names are wire-compatibility identifiers. The broad `Any()` for `Announcement_v2` provides flexibility but moves validation into `common.py`, `client.py`, and `server.py`. Comments still describe removed v1 behavior for historical compatibility context; new code should assume signed v2 announcements.

### Test Signals
`test_introducer.py` and `test_multi_introducers.py` exercise the protocol through real `IntroducerClient` and `IntroducerService` instances. Version-negotiation tests ensure clients reject servers without v2 support.
