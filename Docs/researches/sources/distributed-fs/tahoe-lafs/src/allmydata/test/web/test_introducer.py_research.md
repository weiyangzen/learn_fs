# sources/distributed-fs/tahoe-lafs/src/allmydata/test/web/test_introducer.py

## Purpose
This module tests the web interface of a Tahoe introducer node. It verifies live introducer WUI rendering, static CSS serving, JSON front-page output, and direct `IntroducerRoot` JSON aggregation for subscriptions and announcements.

## Important APIs, Types, And Functions
`create_introducer_webish(reactor, port_assigner, basedir)` creates a node directory, writes `tahoe.cfg`, creates an introducer with `create_introducer`, starts its webish service, and returns the node/service. `IntroducerWeb` drives live HTTP requests through assigned same-process endpoints. `IntroducerRootTests` instantiates `_IntroducerNode`, manipulates its introducer service internals, and renders `IntroducerRoot` in-process.

## Control Flow
The live tests allocate Foolscap and web endpoints, start the introducer service, issue HTTP GETs to `/`, `/tahoe.css`, and `/?t=json`, then parse HTML or JSON. HTML assertions check welcome text, favicon, render-time text, imported-code text, version text, peer/subscriber summaries, and CSS link. JSON assertions check empty summary dictionaries for a fresh node. The unit-style root test adds fake subscribers and a fake announcement, renders JSON, and asserts per-service counts.

## State And Persistence
The helper writes a temporary node directory and `tahoe.cfg`, opens same-process endpoints, starts/stops services, and uses Foolscap eventual queue cleanup. The direct root test mutates in-memory introducer service subscriber and announcement collections.

## Dependencies And Integration Points
Dependencies include Twisted Deferreds/reactor, Foolscap `Tub` and eventual queue, Tahoe node configuration, introducer creation, `_IntroducerNode`, `IntroducerRoot`, `WebishServer`, `SameProcessStreamEndpointAssigner`, `do_http`, `render`, BeautifulSoup, and common soup assertions.

## Risks And Test Signals
Signals include introducer web startup, WUI text/link compatibility, CSS route availability, JSON summary shape, and service-type aggregation. Risks are live-reactor cleanup sensitivity, reliance on internal `_announcements` structure in the root test, and limited coverage of real signed announcement publishing.
