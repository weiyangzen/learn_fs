# sources/distributed-fs/tahoe-lafs/src/allmydata/immutable/encode.py

## Purpose
Encodes encrypted immutable file data into erasure-coded shares, uploads blocks and hash trees to storage bucket writers, constructs URI extension metadata, enforces upload happiness after shareholder failures, and returns a CHK verifier capability.

## Important APIs, Types, And Functions
`UploadAborted` marks user-requested aborts. `Encoder` implements `IEncoder`.

Setup APIs: `set_encrypted_uploadable(uploadable)` reads size, encoding parameters, and storage index from an `IEncryptedUploadable`; `_got_all_encoding_parameters()` configures required/min-happiness/total shares, segment size, CRS encoder/tail encoder, share size, and URI extension base fields. `set_shareholders(landlords, servermap)` installs `IStorageBucketWriter`s and share placement map.

Upload APIs: `start()` builds a Deferred chain: put headers, encode/send each segment, finish hashes, send ciphertext hash tree, block hash trees, share hash trees, URI extension, close shareholders, then return verifier cap. `_encode_segment()`, `_gather_data()`, `_send_segment()`, `send_block()`, and `_remove_shareholder()` perform segment work and failure handling.

Finalization APIs: `finish_hashing()`, `send_crypttext_hash_tree_to_all_shareholders()`, `send_all_block_hash_trees()`, `send_all_share_hash_trees()`, `send_uri_extension_to_all_shareholders()`, `close_all_shareholders()`, `done()`, `err()`, and getters for shares/times/UEB/hash/size.

## Control Flow
After setup, `start()` ensures a reactor turn before work, starts all bucket writers, loops over all non-tail segments and the tail segment, and inserts turn barriers between segments to reduce Deferred retention. Each segment reads exact encrypted data pieces, updates segment and whole-file ciphertext hashers, encodes through CRS, sends each produced block to its landlord if assigned, and records block hashes per share.

After all segments, the encoder finalizes crypttext hash, uploads complete ciphertext hash tree to each live shareholder, builds and uploads one block hash tree per share, builds a share hash tree from block tree roots and uploads only each share's needed proof nodes, packs URI extension metadata, uploads it, and closes bucket writers. `done()` returns `CHKFileVerifierURI(storage_index, uri_extension_hash, k, N, file_size)`.

On shareholder errors, `_remove_shareholder()` aborts that bucket writer, removes it from landlord/servermap state, recomputes servers-of-happiness, and raises `UploadUnhappinessError` if remaining placement no longer satisfies `min_happiness`. `err()` aborts all remaining shareholders and unwraps `DeferredList` first errors.

## State And Persistence
Encoder state is process-local until bucket writers persist data remotely. It tracks `uri_extension_data`, codec instances, upload status, abort flag, encoding parameters, landlords, servermap, block hash lists, share root hashes, crypttext hashes, timing metrics, and placed shares. Remote side effects are append-ordered writes to storage bucket writers: header, blocks, crypttext hashes, block hashes, share hashes, UEB, close/abort.

## Dependencies And Integration Points
Depends on Twisted Deferreds, Foolscap `fireEventually`, `CRSEncoder`, Tahoe URI and hash utilities, `HashTree`, storage bucket writer interfaces, upload status, `happinessutil.servers_of_happiness`, and `UploadUnhappinessError`. Server selection/upload code creates the encoder and passes landlords/servermap; downloader/checker validate the UEB/hash-tree layout it writes.

## Risks And Edge Cases
`segment_size` must be divisible by required shares. Tail encoding pads encrypted data to a multiple of `k` and must match downloader tail calculations. The code intentionally generates all shares to compute roots even if not all shares have landlords. Upload abort only takes effect before/during next data gather and TODO notes it is too late after final segment shares are sent. `_gather_responses()` avoids swallowing non-happiness errors but consumes `UploadUnhappinessError` to let DeferredList semantics work. Long uploads rely on bucket writers preserving append order.

## Test Signals
`src/allmydata/test/test_encode.py` targets UEB/encoding details. `src/allmydata/test/test_upload.py` covers encoder bucket aborts, shareholder failure, happiness enforcement, placement interactions, and upload result behavior. Codec tests cover CRS primitives.
