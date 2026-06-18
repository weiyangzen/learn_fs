<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/test/mutable/test_checker.py -->
## sources/distributed-fs/tahoe-lafs/src/allmydata/test/mutable/test_checker.py

Purpose: Tests mutable-file checker and verifier behavior for SDMF and MDMF files under missing shares, insufficient shares, corrupted signatures, corrupted blocks, corrupted share hashes, and corrupted encrypted private keys.

Important APIs and functions: `Checker` inherits `AsyncTestCase`, `CheckerMixin`, and `PublishMixin`. Test methods call `_fn.check(Monitor(), verify=...)`, `publish_mdmf`, `publish_sdmf`, `corrupt`, and checker mixin assertions such as `check_good`, `check_bad`, and `check_expected_failure`.

Control flow: `setUp` publishes one mutable file. Each test mutates fake storage directly or via `corrupt`, then runs check or verify. Non-verify checks are expected to miss raw block corruption, while verify paths read enough share data to find block hash, share hash, signature, and private-key problems. Empty SDMF/MDMF files are verified and then flush Foolscap eventual events.

State and persistence: Uses fake in-memory storage from `.util`; tests clear or edit `_storage._peers` share dictionaries. No durable filesystem state.

Dependencies and integration points: Exercises Tahoe mutable checker/verifier, `Monitor`, `CorruptShareError`, Foolscap eventual queue flushing, and the shared publish/corruption helper layer.

Risks: Tests depend on exact storage layout labels such as `share_data`, `block_hash_tree`, `share_hash_chain`, and `enc_privkey`. Read-only verification intentionally cannot validate encrypted private-key corruption, so behavior differs by cap authority.

Test signals: Healthy files stay recoverable; no/insufficient shares are bad; verify detects byte-level corruption; checker-only mode does not inspect all block data; readonly nodes treat private-key corruption as uncheckable; empty mutable files verify cleanly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/test/mutable/test_checker.py -->
