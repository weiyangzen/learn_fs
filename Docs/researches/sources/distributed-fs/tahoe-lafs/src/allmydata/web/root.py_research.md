# sources/distributed-fs/tahoe-lafs/src/allmydata/web/root.py

## Purpose
Defines the main client-node web root and top-level WebAPI routing. It mounts capability, file-download, status, statistics, incident-reporting, private, and static resources, renders the welcome page, and emits a JSON summary of introducer and storage-server connectivity.

## Important APIs, Types, And Functions
`URIHandler` handles `/uri` and `/cap` creation, redirect, and capability traversal. `FileHandler` handles `/file` and `/named` download-only file-cap paths. `IncidentReporter` records user-triggered incidents. `Root` installs children and renders HTML/JSON. `RootElement` fills `welcome.xhtml` with node identity, introducer/helper/storage status, service rows, incident form, version, import path, and render time. Helpers include `_describe_known_servers`, `_describe_server`, `_describe_server_and_connection`, and `_describe_connection_status`.

## Control Flow
`Root.__init__` mounts `/uri`, `/cap`, `/private`, `/file`, `/named`, `/status`, `/statistics`, `/report_incident`, and static assets. Dynamic `getChild` returns helper and storage status resources because those services may attach after root construction. `/uri` GET with `uri=<cap>` validates and redirects to `/uri/<cap>` preserving other query args; PUT/POST without a child create unlinked files or directories via `unlinked.py`; child traversal parses a cap and delegates to `directory.make_handler_for`. `/file/<filecap>/...` only permits GET/HEAD and returns a download handler. Root JSON describes introducer connection summaries and known storage servers.

## State And Persistence
The root stores the client and optional time provider. Persistent effects are delegated: unlinked uploads create grid objects, incident reports go through Tahoe logging, and private routes expose live log streams. The root itself does not persist state. Welcome rendering reads live service state from storage, helper, uploader, introducer connection statuses, and storage broker.

## Dependencies And Integration Points
This is the central integration point for `filenode.py`, `directory.py`, `unlinked.py`, `status.py`, `storage.py`, `private.py`, `common.add_static_children`, Tahoe URI parsing, and client service APIs. It depends on Twisted resources/templates and Hyperlink URL handling. Test coverage is in `src/allmydata/test/web/test_root.py`, `test_web.py`, `test_grid.py`, `test_private.py`, `test_status.py`, and broader system tests.

## Risks And Test Signals
Risk areas include capability parsing and URL quoting for `/uri?uri=...` redirects, ensuring `/file` rejects directory caps and non-GET/HEAD methods, delayed storage/helper service lookup, exposing private resources only through auth wrapping, and bytes/str handling in version/server JSON. Test signals include root HTML renderability, JSON schema, top-level child routing, `/uri` upload/mkdir variants, `/file` download route behavior, helper/storage dynamic pages, incident POST method restriction, and reverse-proxy-sensitive URL generation.
