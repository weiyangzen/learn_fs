# sources/distributed-fs/tahoe-lafs/src/allmydata/immutable/downloader/segmentation.py

## Purpose
Adapts arbitrary `read(offset, size)` requests into sequential segment downloads and implements Twisted `IPushProducer` flow control for the consumer.

## Important APIs, Types, And Functions
`Segmentation(node, offset, size, consumer, read_ev, logparent=None)` tracks remaining requested byte range, active segment number, cancel handle, consumer hunger/paused state, read status event, and completion Deferred.

Methods implementing behavior are `start()`, `_maybe_fetch_next()`, `_fetch_next()`, `_got_segment()`, `_retry_bad_segment()`, `_error()`, `stopProducing()`, `pauseProducing()`, and `resumeProducing()`.

## Control Flow
`start()` registers itself as a streaming producer and begins fetching. `_fetch_next()` chooses segment 0 for offset 0 or divides the current offset by actual or guessed segment size. It calls `DownloadNode.get_segment()`, tracks the cancel handle, and attaches callbacks.

`_got_segment()` verifies the returned `(segment_start, segment)` overlaps the next desired byte. If it does not include the current offset, it raises `WrongSegmentError`. Otherwise it slices the desired bytes, updates remaining offset/size, writes to the consumer, updates status, and maybe fetches the next segment.

If the initial segment size was guessed, `_retry_bad_segment()` traps `WrongSegmentError` and `BadSegmentNumberError`, asserts actual segment size is now known, and retries once. Producer flow control toggles `_hungry`; `stopProducing()` cancels outstanding segment requests and errbacks with `DownloadStopped`.

## State And Persistence
State is per read call and non-persistent. It mutates the remaining offset/size as bytes are delivered, and records pause time/decrypted-byte progress through `read_ev`.

## Dependencies And Integration Points
Depends on Twisted Deferreds and `IPushProducer`, Foolscap `eventually`, `allmydata.util.spans.overlap`, `DownloadStopped`, and exceptions from `common.py`. It is created by `DownloadNode.read()` and calls back into `DownloadNode.get_segment()`.

## Risks And Edge Cases
Wrong guessed segment size costs an extra round trip, especially for offset reads. Consumer `write()` can pause the producer reentrantly, so `_maybe_fetch_next()` must respect `_hungry`. `stopProducing()` errbacks the read Deferred; callers must handle cancellation. Returned segment data must cover exactly the next requested byte or the read cannot progress.

## Test Signals
`src/allmydata/test/test_download.py` contains coverage for `_retry_bad_segment`, range slicing, stopped downloads, and consumer flow-control behavior through higher-level download tests.
