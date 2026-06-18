# sources/distributed-fs/tahoe-lafs/src/allmydata/immutable/checker.py

## Purpose
Implements immutable CHK file checking and optional full verification. It can either ask servers which shares they claim to hold or download and cryptographically validate UEB metadata, hash trees, and every block in each share.

## Important APIs, Types, And Functions
Integrity exceptions classify UEB and hash failures: `IntegrityCheckReject`, `BadURIExtension`, `BadURIExtensionHashValue`, `BadOrMissingHash`, and `UnsupportedErasureCodec`.

`ValidatedExtendedURIProxy` wraps a `ReadBucketProxy` and `CHKFileVerifierURI`, fetches the URI extension block, verifies its hash against the verifycap, parses fields with `uri.unpack_extension`, computes segment/block/tail sizes, validates optional/redundant fields, and records mandatory `segment_size`, `crypttext_root_hash`, and `share_root_hash`.

`ValidatedReadBucketProxy` validates server bucket data. `get_all_sharehashes`, `get_all_blockhashes`, and `get_all_crypttext_hashes` fetch and validate complete hash-tree material for verifier mode. `get_block(blocknum)` fetches share hashes, block hashes, and block bytes needed for one block, then `_got_data()` validates share tree, block tree, and block hash.

`Checker` orchestrates server queries. `_get_buckets()` optionally renews leases and gets share buckets. `_download_and_verify()` fully verifies one share. `_verify_server_shares()` verifies all shares from one server. `_check_server_shares()` only trusts reported buckets. `_format_results()` builds `CheckResults`.

## Control Flow
`Checker.start()` maps connected servers through either `_verify_server_shares()` or `_check_server_shares()` and gathers all results before formatting. Lightweight check calls `get_buckets`, wraps claimed sharenums, and records server response status.

Full verification opens each bucket through immutable layout, validates the UEB, seeds a share hash tree with the UEB root, validates all share hashes, all block hashes, and all ciphertext hashes, then sequentially downloads every block and discards its bytes after validation. Remote/storage failures are converted to `(False, sharenum, reason)` tuples for diagnostics; unexpected local failures propagate.

`_format_results()` aggregates verified shares by share number and server, corrupt and incompatible locators, responding servers, health (`all total_shares present`), recoverability (`needed_shares present`), good hosts, and servers-of-happiness.

## State And Persistence
No durable state is written. The checker holds verifycap, server list, monitor, add-lease flag, derived file renewal/cancel secrets, and per-check temporary hash trees. Lease renewal may update remote storage-server lease state through `add_lease`.

## Dependencies And Integration Points
Depends on Twisted Deferreds, Foolscap remote errors, CHK URI types, immutable layout bucket proxies, Tahoe codec parsing, hash utilities, `hashtree.IncompleteHashTree`, `CheckResults`, and `servers_of_happiness`. `filenode.CiphertextFileNode.check()` and `check_and_repair()` instantiate `Checker`; repair consumes its `CheckResults`.

## Risks And Edge Cases
The checker waits for all server Deferreds, so a server that neither fails nor completes can stall checks. Full verify can be expensive because it downloads every block and all hash trees. UEB validation rejects unsupported erasure codec names and inconsistent redundant fields, while normal download ignores those redundant fields. Lease-renewal failures are deliberately tolerated for known old-server errors. A malformed but signature-valid UEB can still trigger assertions in downstream size calculations.

## Test Signals
`src/allmydata/test/test_encode.py` covers `ValidatedExtendedURIProxy`. Download corruption tests in `test_download.py` exercise hash and layout failures. `test_deepcheck.py`, `test_repairer.py`, and immutable filenode tests exercise checker/recoverability integration.
