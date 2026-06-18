# sources/distributed-fs/tahoe-lafs/src/allmydata/test/test_storage_web.py

## Purpose

This file tests Tahoe-LAFS storage-server web/status behavior, especially the interaction between `StorageServer`, the bucket-counting crawler, the lease-checking/expiration crawler, and `allmydata.web.storage.StorageStatus`. It verifies both HTML and JSON status surfaces, crawler progress and persistence state, old crawler-state migration from pickle to JSON, corrupt-share reporting, disk-space reporting, and rendering helpers.

The tests are integration-heavy unit tests: they instantiate real `StorageServer` services in temporary storage directories, create immutable and mutable shares directly through storage-server APIs, manipulate lease timestamps, run Twisted services/crawlers, and render the web status resource or element.

## Important APIs, Types, and Helpers

`remove_tags`, `renderSynchronously`, `renderDeferred`, and `renderJSON` are local rendering helpers. They normalize rendered HTML for substring assertions and render `StorageStatusElement` through Twisted `flattenString`, or render `StorageStatus` with `t=json` through `.common_web.render`.

`MyBucketCountingCrawler` subclasses `BucketCountingCrawler` to fire test hook Deferreds from `finished_prefix`. `MyStorageServer.add_bucket_counter` installs this crawler so `test_bucket_counter_eta` can inspect ETA behavior at exact prefix-completion points.

`InstrumentedLeaseCheckingCrawler` subclasses `LeaseCheckingCrawler` to force controlled yielding after the first bucket. `No_ST_BLOCKS_LeaseCheckingCrawler.stat` returns an `os.stat`-like object with `st_blocks` removed to exercise disk-byte fallback behavior. `InstrumentedStorageServer` and `No_ST_BLOCKS_StorageServer` inject those crawler classes through `LeaseCheckerClass`.

`LeaseCrawler.make_shares` is the central fixture builder. It creates two immutable and two mutable shares using `StorageServer.allocate_buckets`, `StorageServer.slot_testv_and_readv_and_writev`, and `StorageServer.add_lease`, with one single-lease and one double-lease share of each mutability type. It records storage indexes, renew secrets, and cancel secrets for later lease manipulation.

`LeaseCrawler.backdate_lease` uses `ShareFile.renew_lease(..., allow_backdate=True)` to rewrite expiration times so age and cutoff-date expiration modes can be tested deterministically.

## Control Flow

`BucketCounter` starts a `service.MultiService` in `setUp` and attaches storage servers to it. `test_bucket_counter` forces the bucket crawler to yield after one prefix, checks the initial "not computed yet" HTML, waits through crawler progress with `fireEventually` and `PollMixin.poll`, then restores `cpu_slice` and verifies final bucket count and next-crawl text. `test_bucket_counter_cleanup` mutates bogus crawler state mid-cycle and verifies the end-of-cycle cleanup removes invalid buckets and samples. `test_bucket_counter_eta` uses hook Deferreds to render after successive prefixes and verify when ETA text becomes available.

`LeaseCrawler` follows a similar service lifecycle but exercises the lease checker. `test_basic` checks pre-cycle state, controlled in-cycle state after the first bucket, HTML progress predictions, completed history, recovered-space counters, lease counts, and JSON keys. The expiration tests then reuse `make_shares`, rewrite lease times, start the crawler, inspect in-cycle predictive HTML, and verify final share deletion or retention.

`test_expire_age` configures `expiration_mode="age"` and `expiration_override_lease_duration=2000`, backdates one lease per share, and expects only single-lease shares to be deleted while double-lease shares survive with one lease. `test_expire_cutoff_date` configures `expiration_mode="cutoff-date"` and verifies that `actual-*`, `original-*`, and `configured-*` recovery counters differ as expected for cutoff semantics. `test_only_immutable` and `test_only_mutable` use `expiration_sharetypes` to prove expiration is scoped by share type.

Other lease-crawler paths cover invalid expiration mode validation, history retention capped to ten cycles, inability to predict remaining recovery when progress is too early, disk-byte fallback without `st_blocks`, corrupt share detection in current and historical JSON/HTML, and migration of old pickle state/history files with the `admin migrate-crawler` command.

`WebStatus` verifies the web status page independent of crawler details. It covers no-server rendering, normal HTML/JSON stats, missing disk stats (`AttributeError`), failed disk stats (`OSError`), correct disk-stat arithmetic with reserved space, readonly storage, reserved-space rendering, and `StorageStatusElement` utility renderers.

## State and Persistence Behavior

The tests intentionally exercise persistent crawler state files under each storage directory. Bucket counting uses `bucket_counter.state`; lease checking uses `lease_checker.state` and `lease_checker.history`, with serializers `_LeaseStateSerializer` and `_HistorySerializer` validating post-migration JSON loads. The migration tests copy real historical pickle fixtures from `test/data`, invoke `migrate_crawler`, and assert that pickle files are replaced or accompanied by JSON-compatible state.

Storage state is on disk under `storage/.../shares`, including immutable share files, mutable share containers, empty buckets, non-share files, and corrupted share bytes. Lease state is persisted inside share files; tests mutate leases through share APIs and then assert post-crawl deletion, lease counts, and recovered byte counters.

Service state is Twisted-driven. Crawler timing is manipulated with `slow_start`, `cpu_slice`, `timer.reset(0)`, subclass hooks, and `fireEventually`, so many assertions depend on a crawler being mid-cycle or just finished.

## Dependencies and Integration Points

The file depends on Twisted Trial, Twisted services, `flattenString`, Foolscap `fireEventually`, Tahoe storage modules (`StorageServer`, `BucketCountingCrawler`, `LeaseCheckingCrawler`, serializers, storage-index path helpers), web storage rendering (`StorageStatus`, `StorageStatusElement`, `remove_prefix`), admin CLI option parsing and `migrate_crawler`, and test utilities (`fileutil`, `hashutil`, `base32`, `pollmixin`, `.common_web.render`).

It integrates storage internals with public operator-facing status pages. Assertions tie crawler state dictionaries to specific HTML phrases and JSON keys, so changes to `allmydata.web.storage` templates, crawler state schemas, serializer migration, share layout errors, or disk-stat handling will surface here.

## Risks and Edge Cases

These tests are timing-sensitive because they force background crawlers into specific progress windows. Changes to crawler scheduling, prefix ordering, progress estimation, or CPU-slice behavior may require updated synchronization. Some expected predictive counts rely on fixed storage-index positions in the crawler ring.

Several tests assert exact state dictionaries and rendered phrases, including large historical pickle-derived structures. Schema changes can cause noisy failures even when user-visible behavior is acceptable. The pickle migration tests are skipped on Windows because the fixture data is not portable there.

Disk-space assertions are platform-aware but still touch platform-dependent `st_blocks` behavior. The explicit no-`st_blocks` subclass covers fallback logic. Corruption tests intentionally log mutable/immutable container version errors and flush them afterward; new logging or error classes can affect Trial error handling.

## Test Signals

Strong signals include successful HTML and JSON rendering for storage status, crawler progress state transitioning from in-cycle to history, expiration deleting exactly the intended shares, lease counts matching single/double lease scenarios, migration of historical crawler pickle data to JSON serializers, and disk-stat failure modes producing safe availability values.

The file itself is test code. Relevant commands would be targeted Trial runs for `allmydata.test.test_storage_web.BucketCounter`, `LeaseCrawler`, and `WebStatus`, with attention to skipped Windows pickle cases and runtime-sensitive crawler polling.
