<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/test/common.py -->
## sources/distributed-fs/tahoe-lafs/src/allmydata/test/common.py

Purpose: Provides broad Tahoe-LAFS test-suite scaffolding: fake file nodes, in-memory introducer records, Twisted endpoint fixtures, corruption helpers, HTTP/error assertions, and Tahoe-specific `testtools`/Trial test case classes.

Important APIs and types: `FakeDisk` models disk accounting and raises `NoSpace`; `MemoryIntroducerClient`, `Subscription`, `Announcement`, and `get_published_announcements` model introducer behavior. `UseTestPlugins`, `AdoptedServerPort`, and `SameProcessStreamEndpointAssigner` install test endpoint parsers and allocate reliable same-process listening endpoints. `FakeCHKFileNode` and `FakeMutableFileNode` implement enough of immutable/mutable node interfaces for web and directory tests. URI helpers create CHK, SDMF, MDMF, and verifier caps. `WebErrorMixin`, `ErrorMixin`, corruption helpers, `ConstantAddresses`, `disable_modules`, `SyncTestCase`, `AsyncTestCase`, `AsyncBrokenTestCase`, and `TrialTestCase` are reused throughout tests.

Control flow: Fixture setup mutates Twisted plugin search paths, pre-binds sockets when possible, writes generated node configuration, and returns Deferred-compatible fake nodes. Fake file nodes resolve reads from in-memory dictionaries and build synthetic check/deep-check results. Corruption helpers parse immutable or mutable share headers and mutate targeted fields. Test cases wrap `testtools` run-test factories in Eliot logging via `EliotLoggedRunTest`.

State and persistence: Most state is in-memory: fake content dictionaries, socket cleanup callbacks, introducer announcements, mutable `file_types`, and `tempfile.tempdir` cleanup. `UseNode` writes introducer/client config under a test `FilePath`; `SameProcessStreamEndpointAssigner` holds bound sockets until teardown. No durable production state is mutated.

Dependencies and integration points: Integrates Twisted reactors/endpoints, `testtools`, `treq`, Tahoe URI/check/storage/mutable interfaces, RSA/Ed25519 helpers, storage clients, upload/download helpers, and `allmydata.test.common_util`. It is a central dependency for Tahoe tests that need fake nodes, async test cases, HTTP assertions, or share corruption.

Risks: Fake nodes only partially implement interfaces and may mask production behavior. `mktemp()` and random port fallback can be collision-prone. Some corruption helpers contain unreachable or suspicious slices, so they should be treated as historical test tools rather than general parsers. `disable_modules` only handles top-level modules and must restore `sys.modules` even on failures. `AsyncBrokenTestCase` signals tests that depend on extra reactor cleanup.

Test signals: Downstream tests should cover fake node upload/download/check behavior, read-only mutable caps, exact corruption outcomes, socket reuse on supported reactors, plugin cleanup, Eliot-wrapped async failures, HTTP error body assertions, and reactor cleanup after async tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/test/common.py -->
