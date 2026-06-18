# sources/distributed-fs/tahoe-lafs/src/allmydata/web/introweb.py

## Purpose
Defines the web root for an introducer node. It renders a human-readable introducer status page and a JSON summary of subscriber and announcement counts, plus static web assets.

## Important APIs, Types, And Functions
`IntroducerRoot` is the `MultiFormatResource` root. It stores the introducer node/service, installs itself as the empty child, adds static children, and renders HTML or JSON. `IntroducerRootElement` fills `introducer.xhtml` with node metadata and sequence rows for announcements and subscribers. Renderers include `node_data`, `announcement_summary`, `client_summary`, `services`, and `subscribers`.

## Control Flow
Construction fetches the service named `introducer` from the node. HTML rendering builds an `IntroducerRootElement`; JSON rendering iterates `get_subscribers()` and `get_announcements()` to count by `service_name`. Template renderers sort announcements by service name/nickname, format subscriber/announcement timestamps with `render_time`, and produce `SlotsSequenceElement` rows.

## State And Persistence
The module owns no durable state. It reads live introducer service state: announcements, subscribers, connection hints, versions, nicknames, tub IDs, and timestamps. It records a node data dict for the duration of one element instance, including rendered time, node ID, Tahoe version, and import path.

## Dependencies And Integration Points
It depends on Twisted templates, `allmydata.__full_version__`, `idlib`, Tahoe JSON byte dumping, and shared web helpers. It is used as the root resource for introducer nodes rather than client nodes, complementing `root.py`. Tests exist in `src/allmydata/test/test_introducer.py` and `src/allmydata/test/web/test_introducer.py`.

## Risks And Test Signals
Risks are mostly representation drift: bytes/str flattening for server IDs, service-name sorting, and JSON counts matching HTML summaries. The root attaches static children, so packaging-resource behavior from `common.add_static_children` matters. Useful tests verify HTML renderability, JSON count fields, empty subscriber/announcement lists, static children, and realistic introducer service fake objects.
