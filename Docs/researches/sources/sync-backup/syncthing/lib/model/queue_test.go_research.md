# sources/sync-backup/syncthing/lib/model/queue_test.go

## Purpose

`queue_test.go` verifies the behavior and performance characteristics of `jobQueue`. It ensures FIFO pop semantics, in-progress tracking, completion removal, bring-to-front reordering, empty/absent operations, and pagination over the combined progress-plus-queued view.

## Important APIs and Test Cases

- `TestJobQueue` covers a mixed lifecycle of pushing four files, popping them, marking them done, pushing them back, bringing queued files to the front, and handling absent `Done`/`BringToFront` calls.
- `TestBringToFront` focuses specifically on ordering after promoting first, middle, and last queued elements. It uses `messagediff.PrettyDiff` for readable order failures.
- `BenchmarkJobQueueBump` measures `BringToFront` cost on 10k files using random file choices.
- `BenchmarkJobQueuePushPopDone10k` measures queue construction and full drain/done throughput for 10k files.
- `TestQueuePagination` validates `Jobs(page, perpage)` for queued-only state, after one file is in progress, and after eight files are in progress.

## Control Flow

The tests instantiate a new queue, call queue methods directly, and check returned progress/queued slices and skip counts after each state transition. Pagination tests create ten files, request several page/per-page combinations, then progressively move files from queued to progress with `Pop`.

## State and Persistence Behavior

The tests verify only in-memory state. They inspect returned copies from `Jobs` and, in `TestJobQueue`, also inspect internal slice lengths for progress and queued. There is no filesystem, DB, or event dependency.

## Dependencies and Integration Points

The test file uses the Go standard testing, rand, slices, fmt, and time packages plus `github.com/d4l3k/messagediff` for human-readable diffs. It reuses `genFiles` from `model_test.go` for benchmark data.

## Risks and Edge Cases Captured

- Bringing the first queued element to front should leave ordering unchanged.
- Bringing the last queued element to front should preserve the relative order of all earlier elements behind it.
- Calling `Done` for a nonexistent file should not mutate queue state.
- Popping from an empty queue should return `ok == false`.
- `Jobs` skip counts must represent the combined progress and queued offset, including out-of-range pages.
- Mixed progress/queued pagination must fill the page from progress first, then queued entries.

## Test Signals

The queue tests provide focused coverage for all exported package-local queue methods. They do not test invalid pagination inputs such as zero or negative values, which remains a caller-contract assumption.
