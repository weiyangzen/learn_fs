# sources/distributed-fs/tahoe-lafs/src/allmydata/immutable/downloader/status.py

## Purpose
Records append-only, mutable-in-place telemetry for immutable downloads: read requests, segment requests, DYHB server probes, block reads, known shares, problems, and miscellaneous timing events.

## Important APIs, Types, And Functions
`ReadEvent`, `SegmentEvent`, `DYHBEvent`, and `BlockRequestEvent` are thin mutator wrappers around event dictionaries. They update finish/success fields and propagate latest timestamps to `DownloadStatus`.

`DownloadStatus` implements `IDownloadStatus`. It allocates a monotonic `counter`, stores storage index/size, and exposes event creation methods (`add_read_event`, `add_segment_request`, `add_dyhb_request`, `add_block_request`, `add_misc_event`) plus interface methods (`get_counter`, `get_storage_index`, `get_size`, `get_status`, `get_progress`, `using_helper`, `get_active`, `get_started`, `get_results`).

## Control Flow
Download components append event dictionaries when work starts and mutate them through event wrapper methods on completion or failure. `get_status()` derives a text status from unfinished and failed segment events. `get_progress()` computes aggregate progress over unfinished reads only. `get_active()` returns true while any read event lacks `finish_time`.

## State And Persistence
All state is in-memory per `CiphertextFileNode`/`DownloadNode`. Event lists are append-only in ordering, but contained dicts are mutated as work progresses. No persistence or pruning is performed here; `History` bounds visible recent status objects.

## Dependencies And Integration Points
Depends on `itertools.count`, `zope.interface`, and `IDownloadStatus`. Used by `DownloadNode`, `ShareFinder`, `Share`, `Segmentation`, `DecryptingConsumer`, web status elements, and CLI/web status tests.

## Risks And Edge Cases
Event dict schemas are implicit and shared with web/status rendering. Progress ignores completed reads, so it returns `1.0` when no reads are currently outstanding even if prior reads failed. `using_helper()` and `get_results()` are placeholders. Lists can grow for long-lived file nodes with many reads.

## Test Signals
`src/allmydata/test/test_download.py` covers status behavior around reads and requests. `src/allmydata/test/web/test_status.py`, `src/allmydata/test/cli/test_status.py`, and web tests render or instantiate `DownloadStatus`.
