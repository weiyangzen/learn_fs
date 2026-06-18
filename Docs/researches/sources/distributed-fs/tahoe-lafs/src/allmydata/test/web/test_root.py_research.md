# sources/distributed-fs/tahoe-lafs/src/allmydata/test/web/test_root.py

## Purpose
This module tests selected root/WUI behaviors: `/uri?uri=` capability redirects, invalid cap errors, service table rendering for minimal storage server announcements, and root JSON rendering when storage servers report mixed available-space values.

## Important APIs, Types, And Functions
`RenderSlashUri` uses `URIHandler`. `RenderServiceRow` builds a minimal `NativeStorageServer`, `StorageFarmBroker`, and fake `_Client`, then renders `RootElement.services_table`. `RenderRoot` builds two fake storage servers and renders `Root` with `?t=json` using a `DummyRequest`. It also uses `create_signing_keypair`, `ConnectionStatus`, `Tag`, `render`, and `assert_soup_has_tag_with_attributes`.

## Control Flow
Valid `/uri?uri=<cap>` input renders a meta-refresh redirect containing the quoted capability. Invalid input renders `Invalid capability`. The service-row test verifies missing optional announcement fields such as nickname and version render as empty strings rather than failing. The root JSON test overrides `DummyRequest` methods, captures writes, parses JSON, and verifies both servers are represented, one with `available_space: null` and one with a numeric value.

## State And Persistence
State is in-memory fake clients, brokers, storage servers, and dummy requests. No files are persisted.

## Dependencies And Integration Points
The module integrates root web resources with storage client announcements, storage broker server listing, Twisted template rendering, URI validation, root JSON serialization, and node public-key requirements on `_Client`-like objects.

## Risks And Test Signals
Signals include valid cap redirect behavior, invalid cap rejection, robust service table rendering with minimal announcements, and JSON compatibility for `None` available space. Risks include limited coverage of full root page HTML, real storage-server connection changes, and custom `DummyRequest` behavior that may differ from a real request.
