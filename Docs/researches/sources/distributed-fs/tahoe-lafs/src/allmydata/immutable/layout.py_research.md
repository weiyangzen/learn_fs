# sources/distributed-fs/tahoe-lafs/src/allmydata/immutable/layout.py

## Purpose

This module defines the on-wire/on-disk layout of Tahoe-LAFS immutable shares and provides bucket proxy implementations for writing and reading those layouts through storage-server remote references. It supports the legacy v1 share format with 32-bit offsets and the v2 format with 64-bit offsets for large shares. It is a low-level compatibility boundary: upload and repair code write through `WriteBucketProxy` instances, while checker/downloader/debug/helper code read through `ReadBucketProxy`.

## Important APIs, Types, and Functions

- `LayoutInvalid`, `RidiculouslyLargeURIExtensionBlock`, and `ShareVersionIncompatible` model parse failures for corrupted or unsupported immutable share bytes.
- `FORCE_V2` is a test hook that forces `make_write_bucket_proxy` to choose the v2 writer even for small files.
- `make_write_bucket_proxy(rref, server, data_size, block_size, num_segments, num_share_hashes, uri_extension_size)` chooses `WriteBucketProxy` first and falls back to `WriteBucketProxy_v2` on `FileTooLargeError`.
- `_WriteBuffer` batches sequential writes. `queue_write` appends data and returns whether the batch threshold has been reached; `flush` returns the current remote offset and byte payload; `get_total_bytes` tracks flushed plus queued bytes.
- `WriteBucketProxy` implements `IStorageBucketWriter` for v1 shares. It computes fixed section offsets, queues header/data/hash/UEB writes, flushes to remote `write`, and finally calls remote `close`.
- `WriteBucketProxy_v2` overrides only offset/header packing, using 8-byte fields and a `0x44` header.
- `ReadBucketProxy` implements `IStorageBucketReader`. It lazily fetches and parses the share header once, then exposes methods for block data, crypttext hashes, optional block hashes, share hashes, and URI extension bytes.

## Control Flow

Write flow starts with offset calculation in `_create_offsets`. For v1, the header starts at `0x24`; for v2, at `0x44`. The uploader then calls `put_header`, `put_block` for every encoded segment/share block, `put_crypttext_hashes`, `put_block_hashes`, `put_share_hashes`, `put_uri_extension`, and `close` in byte order. `_queue_write` asserts that each requested offset equals the buffer's current total, enforcing a no-hole sequential write discipline. When the batch threshold is reached, `_actually_write` flushes queued bytes to `rref.callRemote("write", offset, data)`. `close` verifies the full allocated size has been queued/written, flushes any remaining bytes, and calls remote `close`.

Read flow begins lazily through `_start_if_needed`. The first read method invokes `_fetch_header`, reads up to the largest header size (`0x44`), and `_parse_offsets` detects version 1 or 2 and unpacks section offsets. Subsequent methods calculate section sizes from adjacent offsets and call remote `read`. `get_uri_extension` reads only the length field first, rejects implausibly large lengths (`>= 2000`), and then reads exactly that UEB payload. `get_share_hashes` validates that the share-hash area is a multiple of the encoded `(2 + HASH_SIZE)` tuple size.

## State and Persistence Behavior

The module itself persists nothing locally; persistence is the remote bucket share written by storage-server calls. Writer state is local and transient: calculated offsets, expected data sizes, segment/hash sizes, and the `_WriteBuffer`. Reader state is also transient: parsed offsets, version, field size/struct, started flag, and a `OneShotObserverList` used to share one header-parse result among concurrent consumers. The actual durable format is the immutable share byte layout documented in the module comments.

## Dependencies and Integration Points

The module depends on Twisted `Deferred`s, Foolscap-like remote bucket references exposing `write`, `close`, `abort`, and `read`, Tahoe interfaces `IStorageBucketWriter`/`IStorageBucketReader`, `HASH_SIZE`, `FileTooLargeError`, `mathutil.next_power_of_k`, and logging/assert helpers. `upload.ServerTracker` uses `make_write_bucket_proxy` both to compute `allocated_size` and to wrap allocated remote bucket writers. `immutable.checker`, downloader share code, helper preflight checks, and debug commands instantiate `ReadBucketProxy` to parse existing shares. The storage server's immutable bucket implementation must accept the offsets and exact write ordering this module emits.

## Risks and Edge Cases

- `_queue_write` requires strict write ordering and no holes. Any future caller that tries random-access bucket writes will fail assertions rather than degrade gracefully.
- The `close` assertion error message references `self._written_buffer`, which does not exist; the assertion condition is still meaningful, but a failure path would raise a misleading secondary `AttributeError` while formatting.
- V1 offsets reject `block_size`, `data_size`, or total offset space at `>= 2**32`; v2 rejects at `>= 2**64`. Boundary tests matter because the selected writer affects compatibility with older Tahoe versions.
- `ReadBucketProxy` trusts parsed offsets enough to derive read sizes; corrupted offset ordering can result in invalid sizes or reads unless caught by downstream validation.
- The hard-coded UEB length sanity cap (`>= 2000`) protects against corrupt lengths but is a protocol assumption that must be updated if legitimate UEBs grow.
- `get_block_hashes` returns `[]` when `at_least_these` is empty, so callers relying on complete block hashes must request at least one hash.

## Test Signals

Relevant coverage appears in `src/allmydata/test/test_storage.py`, which imports `WriteBucketProxy`, `WriteBucketProxy_v2`, `ReadBucketProxy`, and `_WriteBuffer` and exercises v1/v2 layout behavior. Debug and downloader integration paths also rely on `ReadBucketProxy`. Additional repair/checker corruption tests in `test_repairer.py` exercise invalid share layouts and UEB/hash-tree corruption through higher-level verification.
