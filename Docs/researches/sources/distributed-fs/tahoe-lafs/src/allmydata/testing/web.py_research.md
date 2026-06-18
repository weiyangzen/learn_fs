# sources/distributed-fs/tahoe-lafs/src/allmydata/testing/web.py

## Purpose

This module provides in-memory testing helpers for code that talks to Tahoe-LAFS through the WebUI using `treq`. It exposes a fake Tahoe root resource and a `treq.client.HTTPClient` wired through `RequestTraversalAgent`, avoiding a real network listener or real Tahoe grid while preserving an HTTP-client-style interface.

## Important APIs, types, and functions

- `__all__` exports `create_fake_tahoe_root` and `create_tahoe_treq_client`.
- `_FakeTahoeRoot` is a Twisted `Resource` with a `/uri` child. `add_data(kind, data)` delegates to the URI handler and returns the generated cap.
- `KNOWN_CAPABILITIES` is derived from `allmydata.uri` classes that expose `BASE_STRING`; it defines accepted capability kind prefixes.
- `capability_generator(kind)` validates a byte capability kind and yields deterministic fake capability strings.
- `_FakeTahoeUriHandler` is an `attr.s` Twisted leaf `Resource` with `data: BytesKeyDict` and per-kind `capability_generators`.
- `_FakeTahoeUriHandler.add_data(kind, data)` type-checks byte inputs, deduplicates by data bytes, generates a cap for new content, stores `cap -> data`, and returns `(fresh, cap)`.
- `_FakeTahoeUriHandler.render_PUT` reads the request body, stores it as `URI:CHK:`, returns the cap, and sets 201 for fresh data or 200 for duplicate data.
- `_FakeTahoeUriHandler.render_POST` supports `t=mkdir-immutable`, stores request bytes as `URI:DIR2-CHK:`, and returns the cap.
- `_FakeTahoeUriHandler.render_GET` accepts either `/uri?uri=<cap>` or `/uri/<cap>`, validates that a cap was supplied and exists in `data`, returns 400 for missing cap, 410 for unknown cap, or the stored bytes.
- `create_fake_tahoe_root()` builds `_FakeTahoeRoot(uri=_FakeTahoeUriHandler())`.
- `_SynchronousProducer` implements `IBodyProducer` for immediate in-memory request bodies, accepting bytes or unwrapping a `FileBodyProducer`.
- `create_tahoe_treq_client(root=None)` creates a `treq.HTTPClient` with `RequestTraversalAgent(root)` and `_SynchronousProducer`.

## Control flow

Test code can call `create_fake_tahoe_root()`, optionally prepopulate it with `root.add_data(kind, data)`, then pass it to `create_tahoe_treq_client`. Requests issued through the returned `HTTPClient` traverse the Twisted resource tree in memory. PUT and POST bodies are synchronously produced, read by the fake URI handler, stored in `BytesKeyDict`, and returned as capability bytes. GET decodes the Twisted request URI with `hyperlink.DecodedURL`, extracts a query cap or path cap, and looks up stored bytes.

## State and persistence behavior

State is entirely in memory. `_FakeTahoeUriHandler.data` maps capabilities to bytes and deduplicates identical bytes by returning the existing cap. `capability_generators` stores one deterministic generator per capability kind so subsequent additions have stable but distinct sizes/caps. There is no disk persistence, real shares, mutable state model, leases, or network transport.

## Dependencies and integration points

The helper integrates Twisted resources and body producers, `treq.client.HTTPClient`, `treq.testing.RequestTraversalAgent`, `hyperlink.DecodedURL`, `attrs`, `zope.interface`, Tahoe URI constants/classes, Tahoe base32 utilities, and `BytesKeyDict`. It is intended for tests of Tahoe WebUI clients that need a lightweight subset of `/uri`.

## Risks and edge cases

- The fake implements only part of `/uri`: PUT immutable upload, POST mkdir-immutable, and GET by cap.
- Capability strings are syntactically plausible and deterministic but not cryptographically tied to content or erasure coding parameters.
- `render_POST` assumes `request.args[u"t"][0]` exists and is supported.
- `_SynchronousProducer` accesses `FileBodyProducer._inputFile`, a private attribute, for testing convenience.
- GET path extraction only uses `request.postpath[0]`, so nested path behavior is intentionally absent.

## Test signals

Useful signals are client code that can PUT bytes, receive a stable cap, GET bytes back by query or path cap, observe 201/200 duplicate behavior, and create immutable-directory-like caps. Tests should avoid treating this fake as a complete WebAPI implementation.
