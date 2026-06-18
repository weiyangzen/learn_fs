# sources/storage-engines/wiredtiger/test/suite/test_layered_delta04.py

Purpose: stress-tests 32 consecutive page deltas across encryption, compression, URI kind, and timestamped versus non-timestamped operation modes.

Important APIs and functions: `test_layered_delta04` uses `DisaggConfigMixin`, compressor and encryptor extension registration, URI scenarios for layered and disaggregated file tables, `page_delta=(delta_pct=100)`, timestamped commits when enabled, repeated checkpointing, and follower reopen with complete checkpoint metadata.

Control flow: the test inserts ten base rows, checkpoints, then runs 32 rounds where key `0` is updated and checkpointed. In timestamped scenarios, follower reads are run at the base timestamp and after every update timestamp. In non-timestamped scenarios, only the latest value is validated.

State and persistence behavior: a compact dataset receives a long sequence of persisted deltas. Timestamped mode verifies historical reconstruction at each point in the delta chain; non-timestamped mode verifies final state. Compression/encryption broaden the physical encoding cases.

Dependencies and integration: depends on page-log delta apply, timestamp visibility, compression/encryption extensions, and both layered and file-backed disaggregated objects. Risks include chain-order errors, historical read regressions, encrypted/compressed delta decoding bugs, and URI-specific differences. Test signals are exhaustive key/value assertions at every relevant timestamp.
