# sources/distributed-fs/tahoe-lafs/src/allmydata/test/test_testing.py

## Purpose

This file tests `allmydata.testing.web`, the verified fake WebAPI test infrastructure. It proves that `create_tahoe_treq_client` behaves enough like Tahoe's WebAPI for tests that need upload/download semantics without a real grid.

The scope is intentionally narrow: fake `PUT /uri` uploads produce CHK caps, repeated uploads are recognized, existing caps can be downloaded, missing caps return HTTP 410, and malformed download requests return HTTP 400.

## Important APIs, Types, and Helpers

`create_tahoe_treq_client` constructs the fake treq-style HTTP client under test. `capability_generator` produces plausible capabilities for missing-data tests. `allmydata.uri.from_string` and `CHKFileURI` validate returned caps.

`FakeWebTest` inherits from `.common.SyncTestCase`, not regular Trial async setup, because Hypothesis is used and the file explicitly avoids `setUp`. Each property-based test creates its own fake client.

The file uses Hypothesis `@given(content=binary())` for arbitrary byte content. Testtools matchers (`Equals`, `IsInstance`, `MatchesStructure`, `AfterPreprocessing`, `Contains`, `Always`) and `testtools.twistedsupport.succeeded` assert Deferred outcomes. `hyperlink.DecodedURL` builds query URLs, and Twisted `GONE` supplies the 410 status constant.

## Control Flow

`test_create_and_download` creates a fake client, uploads arbitrary bytes with `PUT http://example.com/uri`, checks status 201, parses the response body as a CHK cap, downloads through `/uri?uri=<cap>`, checks status 200, and verifies round-tripped content. The comment says the `/uri/<cap>` form is valid, but the implementation repeats the query-argument form.

`test_duplicate_upload` uploads the same arbitrary content twice. The first response must be 201 with a CHK cap body; the second must return 200, proving the fake tracks already-uploaded content/caps.

`test_download_missing` generates a CHK-looking cap that the fake has not stored, issues a GET with `?uri=...`, and asserts a succeeded response with status 410 and content containing `No data for`.

`test_download_no_arg` calls `/uri/` without a `uri` query argument and expects status 400.

## State and Persistence Behavior

All state is in-memory inside the fake treq client for the lifetime of each test. There is no filesystem persistence. The duplicate-upload test demonstrates that the fake maintains an upload map from content/capability to stored bytes. Hypothesis-generated cases are isolated because each test constructs a fresh client inside the test body.

## Dependencies and Integration Points

The file integrates testing helpers with Tahoe URI parsing and a treq-like response API (`code`, `content()`, `put`, `get`). Downstream tests that rely on `create_tahoe_treq_client` can use these guarantees when they need deterministic fake WebAPI behavior.

It depends on Twisted Deferreds through `inlineCallbacks`, testtools Deferred matchers, Hypothesis, hyperlink URL construction, and Tahoe URI classes.

## Risks and Edge Cases

The fake is deliberately smaller than the real WebAPI. These tests only cover CHK upload/download behavior and a couple of error statuses; they do not cover directory APIs, mutable caps, streaming semantics, headers, content types, authorization, or alternate `/uri/<cap>` path behavior despite the comment.

Because Hypothesis can generate empty and arbitrary binary content, the fake's content storage and cap generation are tested across byte edge cases. However, without a fixed example database or explicit settings in this file, runtime and shrinking behavior follow project/global Hypothesis configuration.

## Test Signals

Passing tests signal that fake WebAPI clients can be used for property tests needing simple upload/download and duplicate detection. The strongest behavioral checks are CHK cap parseability, byte-for-byte round trips for arbitrary bytes, 201-vs-200 duplicate semantics, and correct 410/400 error statuses.
