# sources/distributed-fs/tahoe-lafs/src/allmydata/test/test_crawler.py

## Purpose
This module tests `allmydata.storage.crawler.ShareCrawler` against a real `StorageServer` share directory. It verifies that crawler subclasses enumerate bucket directories, persist and resume prefix/cycle progress, respect service lifecycle scheduling, expose progress/state before and during work, and can stop themselves after a single cycle.

## Important APIs, types, and functions
- `BucketEnumeratingCrawler`, `PacedCrawler`, `ConsumingCrawler`, and `OneShotCrawler` are local `ShareCrawler` subclasses used to exercise extension hooks: `process_bucket`, `finished_cycle`, and `yielding`.
- `Basic.setUp` and `tearDown` manage a Twisted `MultiService` parent, so storage servers and crawler services run under real service lifecycle semantics.
- `Basic.write` allocates one storage bucket through `StorageServer.allocate_buckets`, writes share data, closes the writer, and returns the base32 storage index string via `si_b2a`.
- Tests call `load_state`, `save_state`, `start_current_prefix`, `get_state`, `get_progress`, `setServiceParent`, and `disownServiceParent` on crawler instances.

## Control flow
The tests create deterministic storage indexes from integer seeds and sometimes mutate the final byte to place multiple buckets under one prefix directory. `test_immediate` drives crawling synchronously with `start_current_prefix` and confirms that a completed cycle resets the statefile to the beginning. `test_service` attaches a crawler to the service tree and waits on a Deferred fired by `finished_cycle`. `test_paced` forces `TimeSliceExceeded` in the middle and end of bucket processing, manually saves state, then constructs new crawler instances to verify resume behavior. `test_paced_service` exercises the scheduled path and checks progress while the crawler yields. `test_empty_subclass` runs the base crawler for coverage of no-op hooks, and `test_oneshot` confirms a crawler can detach from its parent after the first completed cycle.

## State and persistence behavior
State lives in the crawler statefile under each test-specific basedir. The tests inspect `last-complete-prefix`, `current-cycle`, `last-cycle-finished`, progress booleans, sleep timers, and remaining wait/sleep times. The most important persistence behavior is resumability after `TimeSliceExceeded`: a crawler that saves state mid-cycle must let a fresh process continue without duplicating or skipping buckets. The tests also validate that a fully completed cycle resets traversal state so later crawlers start from the beginning.

## Dependencies and integration points
The module depends on Twisted Trial, Twisted services, Foolscap `eventually`/`fireEventually`, Tahoe `StorageServer`, `ShareCrawler`, storage-index hash helpers, filesystem helpers, and polling/stall utilities from Tahoe tests. It integrates crawler behavior with actual storage server layout rather than mocking the share tree.

## Risks
Timing-sensitive assertions in `test_paced_service` depend on deterministic share ordering and expected completion percentage after six buckets. The disabled CPU-usage test documents that wall-clock and host load make strict CPU throttling tests unreliable. Resume correctness is also fragile around boundaries where a timeslice expires inside `process_bucket` versus immediately after a bucket.

## Test signals
Useful regression signals are complete bucket-set equality, correct progress flags before first tick and during a yield, persisted resume across new crawler instances, timer/sleep fields after service-driven completion, base-class cycle completion, and one-shot shutdown with no further counter increments after disowning the service parent.
