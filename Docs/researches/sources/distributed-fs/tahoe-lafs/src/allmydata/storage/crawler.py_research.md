# sources/distributed-fs/tahoe-lafs/src/allmydata/storage/crawler.py

## Purpose
Implements rate-limited background traversal of storage-server shares, plus JSON state serialization/migration helpers and a bucket-counting crawler.

## Important APIs, Types, and Functions
Defines `TimeSliceExceeded`, `MigratePickleFileError`, conversion helpers `_convert_cycle_data()`, `_convert_pickle_state_to_json()`, `_upgrade_pickle_to_json()`, `_confirm_json_format()`, `_dump_json_to_file()`, `_LeaseStateSerializer`, `ShareCrawler`, and `BucketCountingCrawler`.

## Control Flow
`ShareCrawler.startService()` schedules a slow-start timer. Each `start_slice()` processes prefixes until `cpu_slice` is exceeded, saves state, computes a sleep interval from `allowed_cpu_percentage`, and schedules the next slice. `start_current_prefix()` initializes cycles, walks sorted 10-bit prefix dirs, delegates to `process_prefixdir()`, tracks progress timing, and calls subclass hooks. `process_prefixdir()` skips already processed buckets and calls `process_bucket()` for subclasses.

## State and Persistence Behavior
Crawler state is JSON persisted through `_LeaseStateSerializer.save()` with temp-file move-into-place. State tracks version, current/last cycle, current cycle start time, last complete prefix, and last complete bucket. Legacy pickle state is rejected by `_confirm_json_format()` unless explicitly upgraded through `_upgrade_pickle_to_json()`. Bucket counting stores per-cycle prefix counts and sample storage indexes, pruning old cycles after completion.

## Dependencies and Integration Points
Depends on Twisted service/reactor, `FilePath`, `fileutil.move_into_place`, and storage-index base32 helpers. Subclasses such as `LeaseCheckingCrawler` attach to `StorageServer` and consume `server.sharedir`.

## Risks and Edge Cases
SIGKILL during a time slice can duplicate work after restart because state is saved at slice/cycle boundaries unless subclasses save more often. Pickle-format files now block startup/migration paths through `MigratePickleFileError`. Timing estimates may be `None` or inaccurate for very fast/slow prefixes. JSON migration must preserve tuple-key structures carefully.

## Test Signals
`src/allmydata/test/test_crawler.py` exercises prefix traversal, pacing, state persistence, resumption, one-shot behavior, and migration-related helpers. `tahoe_run.py` handles `MigratePickleFileError` as a startup error.
