# sources/distributed-fs/tahoe-lafs/src/allmydata/test/mutable/test_roundtrip.py

## Purpose
This file tests end-to-end mutable servermap update and retrieval behavior after ordinary publishing and deliberate share corruption. It verifies that SDMF and MDMF downloads either recover content or fail with the expected Tahoe error and diagnostic message when every usable share is damaged.

## Important APIs, Types, And Functions
`Roundtrip` inherits `AsyncTestCase`, `ShouldFailMixin`, and `PublishMixin`. Core helpers are `make_servermap`, `do_download`, `_test_corrupt_all`, `_test_corrupt_some`, and the servermap debugging helpers `abbrev_verinfo`, `abbrev_verinfo_dict`, and `dump_servermap`. It uses `ServerMap`, `ServermapUpdater`, `Retrieve`, `Monitor`, `MemoryConsumer`, `NotEnoughSharesError`, `UnrecoverableFileError`, `MODE_READ`, `make_storagebroker`, and `corrupt`.

## Control Flow
`setUp` publishes an initial mutable file. Basic tests build a servermap, retrieve through `Retrieve.download`, reuse the same map, update the old map, and force public-key refetch by clearing `self._fn._pubkey`. Failure tests remove shares or substitute an empty storage broker. Corruption tests flip bytes at logical layout offsets before or after servermap creation, then download with or without `fetch_privkey` and assert either successful plaintext or a specific failure substring.

## State, Persistence, And Dependencies
All storage is the in-memory `FakeStorage` from `mutable/util.py`. Corruption is layout-aware through `MDMFSlotReadProxy.get_verinfo` in the shared helper, so tests depend on mutable share offset names such as `pubkey`, `signature`, `share_hash_chain`, `block_hash_tree`, `share_data`, and `enc_privkey`. The tests integrate with the mutable downloader retry path and servermap problem recording.

## Risks And Test Signals
The strongest signals are around corrupted metadata, hashes, public keys, signatures, encrypted private keys, and late corruption after map update. The file also checks no-server recovery after a failed download. A disabled `OFF_test_corrupt_all_seqnum_late` documents an unresolved gap: retrieve does not yet check the checkstring on each block fetch.
