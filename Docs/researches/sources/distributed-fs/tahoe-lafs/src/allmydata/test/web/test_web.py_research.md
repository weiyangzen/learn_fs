# sources/distributed-fs/tahoe-lafs/src/allmydata/test/web/test_web.py

## Purpose

This is the main Tahoe-LAFS WebAPI/WebUI integration-style test module. It builds a minimal fake Tahoe client, fake uploader, fake node maker, fake history, fake storage server, and a real `webish.WebishServer`, then exercises HTTP behavior through `treq`/Twisted. The file validates welcome/status/storage pages, security headers, file and directory URL handling, mutable and immutable upload flows, JSON/HTML/text/API formats, operation handles, redirects, ETags, range requests, static serving, incident reporting, and error humanization.

## Important APIs, types, and helpers

- `FakeStatsProvider`, `FakeBucketCounter`, `FakeLeaseChecker`, and `FakeStorageServer` provide enough service/stat state for WebUI pages to render storage and lease status.
- `FakeNodeMaker` subclasses `NodeMaker` and creates `FakeCHKFileNode` / `FakeMutableFileNode` instances backed by a shared `all_contents` dictionary. Its `encoding_params` fix `k=3`, `n=10`, `happy=7`, and a 128 KiB segment size for predictable tests.
- `FakeUploader.upload` reads uploadable data, creates a fake CHK file node, stores data in `all_contents`, and returns an `upload.UploadResults` with fake timings/share metadata and the generated URI.
- `build_one_ds` constructs a `DownloadStatus` with segment, DYHB, read, and block events in complete, error, and unfinished states so status views can render mixed operation progress.
- `FakeHistory` exposes lists of upload/download/mapupdate/publish/retrieve statuses consumed by `/status`.
- `FakeDisplayableServer` supplies display-oriented storage server state, announcements, connection status, version, nickname, available space, and timestamps for welcome JSON/HTML tests.
- `FakeClient` subclasses `_Client` but avoids full client initialization. It wires together fake node maker/uploader/history/storage broker, two known storage servers, node identity, nickname, introducer/helper state, and a `SecretHolder`.
- `WebMixin` is the shared fixture. `setUp` starts `FakeClient` and `webish.WebishServer`, creates public/private roots and a nested directory tree, stores sample CHK/SDMF/MDMF files, special Unicode/HTML-sensitive names, read-only directories, and broken content references. It exposes HTTP helpers `GET`, `HEAD`, `PUT`, `DELETE`, `POST`, `POST2`, multipart `build_form`, failure helpers, node/content assertion helpers, operation polling helpers, redirect helpers, and initial-child builders.
- `MultiFormatResourceTests` defines an inline `MultiFormatResource` subclass and tests format selection, default format behavior, explicit `None` renderer fallback, and unknown-format errors.
- `Web` contains the large behavioral test suite.
- `HumanizeExceptionTests` verifies `humanize_exception` maps `MustBeReadonlyError` to 400 and `FileTooLargeError` to 413.

## Control flow and behavior covered

The fixture creates a real listening Webish service with an in-memory Tahoe graph. Most tests make HTTP requests against `self.webish_url`, parse responses, then assert either HTTP headers/body/status or resulting fake node state.

High-level WebUI coverage includes root page security headers; welcome JSON and HTML server, introducer, and helper status; `/storage`; `/status`; CSS and static files; and `/report_incident`.

File URL coverage includes GET/HEAD/range semantics, named cap URLs, `/uri/<filecap>`, MDMF suffixes, read-only cap mutation rejection, ETags, and `t=json|uri|readonly-uri|info` outputs.

Directory URL coverage includes HTML listings, forms, read-only markers, encoded unsafe names, literal immutable directories, JSON metadata, manifests, deep-size/deep-stats, stream-manifest, deep-check, check, and repair operations.

Mutation and upload coverage includes PUT/POST file upload, mutable and immutable creation, format selection, mkdir/mkdir-with-children/mkdir-immutable, parentless `/uri` operations, URI linking, unknown cap policy, set-children, delete/unlink, rename/relink, replace policies, and mutable offset updates.

Operation-handle coverage includes bad handles, cancel, `retain-for`, `release-after-complete`, uncollected expiration after four days, collected expiration after one day, and a redirect regression for `/uri/?uri=<cap>&t=json`.

## State and persistence behavior

All filesystem-like state lives in fake in-memory nodes backed by `FakeClient.all_contents`. Directory mutations update fake `DirectoryNode`/mutable node structures; immutable file contents are keyed by cap in `all_contents`; mutable content is stored by fake mutable nodes. The Webish server also has a temporary directory from `anonymous_tempfile_factory` for request bodies and a `staticdir` for static file tests. Operation-handle state is held by the Webish `operations` service and time-dependent expiration is controlled with a Twisted `Clock` plus `fakeTime` for deterministic rendering.

Persistent external effects are deliberately limited to temp files created by Trial/Twisted for the server, static file fixture content, and request temp bodies. No real Tahoe grid, introducer, storage server, or network storage persistence is used.

## Dependencies and integration points

The tests integrate with Twisted services/Deferreds/Trial/HTTP, `treq`, BeautifulSoup/html5lib, Tahoe `webish`, `web.common.MultiFormatResource`, `_Client`, `SecretHolder`, storage broker/server fakes, node maker, directory nodes, immutable/mutable status classes, fake test nodes, URI parsing, mutable key derivation, JSON/base32/hash helpers, connection status, and web test helpers. The module is a broad contract for Webish, root resources, file/directory web resources, operation-monitor resources, upload/mkdir command parsing, and exception-to-HTTP mapping.

## Risks and edge cases

- The fixture validates WebAPI control flow and representation but not real erasure coding, storage allocation, network introducer behavior, or durable storage.
- Exact HTML/form/CSS assertions catch regressions but can make UI refactors expensive.
- Some fixture setup assumes fake node operations are synchronous.
- `FakeClient` bypasses `_Client.__init__`, so Webish/client interface changes may require fixture updates.
- URI/capability security is central: tests cover secret censoring, unknown rw-cap rejection, readonly/immutable prefix handling, and read-only mutation errors.
- Operation-handle expiry depends on deterministic fake-clock behavior.

## Test signals

This file is itself a dense test signal for the WebAPI. Strongly covered areas are HTTP method routing, response formats, mutable/immutable format selection, path handling, redirects, operation handles, range/ETag semantics, JSON metadata, unknown-cap policy, and WebUI rendering. Weaker signals are real storage interaction, concurrency/race behavior, browser-level rendering, and production filesystem persistence.
