# sources/distributed-fs/tahoe-lafs/src/allmydata/test/test_hung_server.py

## Purpose
Tests downloader behavior when storage servers are broken, missing shares, or hung. It uses `GridTestMixin` to simulate Tahoe storage without real network services and covers immutable behavior fully, with mutable hung-server cases explicitly skipped as known broken.

## APIs / Types / Functions
- `HungServerDownloadTest` mixes `GridTestMixin`, `ShouldFailMixin`, `PollMixin`, and Trial `TestCase`.
- `_set_up` builds a grid, uploads immutable `upload.Data` or mutable `MutableData`, records `self.uri`, `self.shares`, `self.servers`, and `self.c0`.
- `_download_and_check`, `_should_fail_download`, `_start_download`, and `_wait_for_data` abstract immutable `download_to_data` versus mutable `download_best_version`.
- Share/server mutators include `_break`, `_hang`, `_unhang`, `_hang_shares`, `_delete_all_shares_from`, `_copy_all_shares_from`, and `_corrupt_share`.

## Control Flow
Most tests chain Deferred callbacks: create a grid, mutate server/share state, then assert download success or failure. The matrix covers healthy shares, copied shares, missing shares, broken servers, duplicate shares, and immutable hung servers. `test_5_overdue_immutable` directly tunes the immutable `ShareFinder`, hangs the first five relevant servers, forces overdue timers, and verifies replacement requests complete the download.

## State And Persistence
The tests manipulate real share files under no-network storage server directories, using `storage_index_to_dir` to copy shares. Runtime state is stored on the test instance, including URI/share maps and the private `_sharefinder` in the overdue test.

## Dependencies / Integration Points
Integrates with immutable upload/download, mutable publishing, no-network grid controls, URI parsing, storage layout, `NotEnoughSharesError`, and `UnrecoverableFileError`.

## Risks And Test Signals
The suite intentionally reaches into private downloader and storage internals, so it is brittle during refactors. The skipped mutable hung tests mark a real coverage gap. Passing tests signal immutable download progress under hung servers, correct failure with insufficient distinct shares, and overdue request replacement behavior.
