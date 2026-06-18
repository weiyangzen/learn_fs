<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/test/mutable/test_filenode.py -->
## sources/distributed-fs/tahoe-lafs/src/allmydata/test/mutable/test_filenode.py

Purpose: Provides broad mutable filenode behavior tests covering creation, cap types, SDMF/MDMF uploads and downloads, streaming retrieval producer behavior, modification semantics, retry/backoff on uncoordinated writes, maximum share counts, and size reporting.

Important APIs and functions: `Filenode` uses `FakeStorage`, `make_peer`, `make_nodemaker_with_peers`, `MutableFileNode`, `MutableData`, `BackoffAgent`, mutable modes, and several consumer fixtures. Key tests include `test_create`, `test_create_with_keypair`, MDMF cap/readcap/verifier-cap tests, `_test_retrieve_producer`, `test_modify`, `test_modify_backoffer`, and `test_size_after_servermap_update`.

Control flow: `setUp` creates fake storage with ten peer wrappers and a nodemaker. Creation tests publish empty or initial-content nodes and inspect storage/servermap state. Upload/download tests chain Deferred operations through servermap retrieval, overwrite, download, explicit upload, version download, and large-file paths. Producer tests read versions into consumers that pause or stop to assert `DownloadStopped`. Modify tests apply modifiers that change, do not change, return `None`, raise ordinary errors, raise `UncoordinatedWriteError`, or exceed historical size limits, then verify contents and sequence numbers.

State and persistence: All storage is fake/in-memory. Node defaults such as `n`, `k`, `happy`, key generator, and node cache are mutated per test. Sequence numbers and servermaps represent mutable-file version state in fake shares.

Dependencies and integration points: Exercises mutable filenode, publisher, retriever, servermap, cap parsing, RSA key generation, Tahoe client key generator, consumer producer interfaces, and async broken test support for lingering reactor work.

Risks: Many assertions rely on fake storage internals such as `_peers`, peer write counts, and sequence-number expectations. `AsyncBrokenTestCase` indicates some paths leave extra reactor activity. Large MDMF tests allocate multi-megabyte byte strings and may be resource-sensitive.

Test signals: Correct cap class selection, one share per peer under default placement, support for one-share and 255-share configurations, MDMF segmented download correctness, producer stop/pause error propagation, modifier idempotence/no-op handling, UCWE retry/backoff behavior, and accurate size after servermap updates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/test/mutable/test_filenode.py -->
