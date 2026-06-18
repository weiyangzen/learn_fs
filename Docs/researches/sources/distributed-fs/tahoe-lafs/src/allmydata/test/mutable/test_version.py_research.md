# sources/distributed-fs/tahoe-lafs/src/allmydata/test/mutable/test_version.py

## Purpose
This file tests version-specific mutable-file behavior: upload protocol selection, sequence numbers, caps returned after upload, readable versus mutable version objects, overwrites, modifies, explicit version download, partial reads, debug-script output, and read/download equivalence for MDMF and SDMF.

## Important APIs, Types, And Functions
`Version` combines `GridTestMixin`, `AsyncTestCase`, `ShouldFailMixin`, and `PublishMixin`. Async helpers include `do_upload_mdmf`, `do_upload_sdmf`, `do_upload_empty_sdmf`, `do_upload`, `_test_partial_read`, `_do_partial_read`, and `_test_read_and_download`. It uses `MutableFileNode`, `MutableData`, `SDMF_VERSION`, `MDMF_VERSION`, `consumer.MemoryConsumer`, `gatherResults`, `mathutil.next_multiple`, Tahoe URI classes, and `allmydata.scripts.debug`.

## Control Flow
`setUp` creates a no-network grid, client, nodemaker, large MDMF data, and small SDMF data. Tests upload files and assert protocol versions, inspect debug `find_shares`, `dump_share`, and `catalog_shares` output, update both file types, compare version object metadata to node metadata, and verify read-only nodes return read-only version objects. Partial-read tests call `version.read` with offsets and sizes including zero-length, `None`, segment boundaries, and full-file coverage.

## State, Persistence, And Dependencies
This file uses real no-network share directories and inspects them through debug commands, so it depends on stable share-file layout and output labels. It also uses `PublishMixin.publish_multiple` to create competing recoverable versions in in-memory storage for explicit `download_version` coverage.

## Risks And Test Signals
It catches capability-type regressions, sequence-number failures after overwrite, incorrect read-only/mutable object semantics, partial-read off-by-one errors, and debug output drift. The debug test is intentionally detailed and may need updates if human-readable debug formatting changes.
