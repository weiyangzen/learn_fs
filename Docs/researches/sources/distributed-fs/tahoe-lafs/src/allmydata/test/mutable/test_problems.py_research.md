<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/test/mutable/test_problems.py -->
## sources/distributed-fs/tahoe-lafs/src/allmydata/test/mutable/test_problems.py

Purpose: Exercises mutable-file failure scenarios around stale servermaps, surprise concurrent writes, unexpected shares, bad or missing servers, private-key query failures, block/hash query failures, and a regression fixture for mutable share hash-tree validation.

Important APIs and types: `SameKeyGenerator` forces deterministic mutable keys. `FirstServerGetsKilled` and `FirstServerGetsDeleted` alter fake server behavior after selected calls. `Problems` uses `GridTestMixin`, `AsyncTestCase`, `ShouldFailMixin`, mutable modes, `MutableData`, `NotEnoughSharesError`, `NotEnoughServersError`, `UncoordinatedWriteError`, URI/hash helpers, storage path helpers, and class-level `TEST_1654_*` fixtures.

Control flow: Surprise tests capture an old servermap, perform a winning overwrite, then attempt upload or download using stale state and expect coordination/share errors. Server placement tests remove, replace, break, or restore servers around publishes and overwrites. Private-key and block/hash query tests install post-call notifiers that make one server fail or appear deleted after initial reads, then verify map update or download can continue. `test_1654` writes crafted two-share data to disk and expects retrieval to fail rather than return corrupted contents.

State and persistence: Uses no-network grid directories and writes fixture shares directly under storage-index paths. Mutates grid membership, server wrapper `broken` flags, nodemaker key generator/cache, server post-call notifiers, and stored share files.

Dependencies and integration points: Integrates mutable publish/retrieve/servermap code, no-network grid server management, Tahoe URI and storage layout helpers, RSA key generation, hash-based cap derivation, Foolscap logging, and file utilities.

Risks: These tests depend on internal fake-grid mechanics and sometimes fixed server query order. Direct disk fixture writes can become stale if storage layout changes. Some failure assertions check substrings, so wording changes can break tests. The large #1654 base64 fixtures are difficult to audit but security-sensitive.

Test signals: Stale publish paths raise `UncoordinatedWriteError`; stale retrieve raises `NotEnoughSharesError`; unexpected share placement is detected; publish succeeds with limited bad servers but fails with all/no servers; privkey/block/hash transient failures are tolerated when enough shares remain; crafted #1654 shares fail retrieval due to corruption detection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/test/mutable/test_problems.py -->
