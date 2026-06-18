# sources/sync-backup/syncthing/lib/model/queue.go

## Purpose

`queue.go` implements `jobQueue`, a small mutex-protected FIFO used by folder pulling code to track files waiting to be pulled and files currently in progress. It provides queue mutation, promotion of a queued file to the front, completion removal, pagination for API/UI reporting, and reset/length helpers.

The queue stores only file names plus size/modification metadata for queued entries. Current code in this file only exposes names; `size` and `modified` are retained in `jobQueueEntry` for possible ordering or metadata use by surrounding puller code.

## Important APIs, Types, and Functions

- `jobQueue` has `progress []string`, `queued []jobQueueEntry`, and a mutex.
- `jobQueueEntry` stores `name`, `size`, and `modified` as Unix nanoseconds.
- `newJobQueue` returns an empty queue.
- `Push` appends a file entry to the queued FIFO.
- `Pop` removes the first queued entry, appends its name to `progress`, and returns the name plus success flag.
- `BringToFront` finds a queued filename and shifts it to queued index zero while preserving the relative order of earlier items behind it.
- `Done` removes a filename from `progress` if present.
- `Jobs` returns paginated progress names, queued names, and the number of skipped items across the combined `progress + queued` view.
- `Reset` clears both slices.
- `lenQueued` and `lenProgress` return counts under lock.

## Control Flow

The expected lifecycle is `Push` for files needing pull, `Pop` when a worker starts a file, and `Done` when the worker finishes or abandons that file. `BringToFront` can be called before `Pop` to prioritize a queued filename. `Jobs` is read-only from the caller's perspective but locks internally, computes the combined pagination window, copies names into fresh slices, and never exposes internal slices.

Pagination treats in-progress jobs as preceding queued jobs. If the requested page starts beyond the total count, it returns nil progress/queued slices and `skipped == total`. If the page falls entirely in progress, only progress is returned. Otherwise it returns the remaining progress names plus enough queued names to fill `perpage`.

## State and Persistence Behavior

All state is in memory and protected by `q.mut`. The queue does not persist to disk or database. It does not deduplicate filenames, so callers are responsible for avoiding duplicate queued entries if that matters. `Done` is idempotent for absent names. `BringToFront` is a no-op when the file is absent or already first.

## Dependencies and Integration Points

`queue.go` depends only on the Go standard library (`sync`, `time`). It is integrated through folder runner/puller code and surfaced through the model's `NeedFolderFiles`, which asks a running folder service for `Jobs(page, perpage)` and then maps returned names back to global `protocol.FileInfo` records.

## Risks and Edge Cases

- Queue ordering is FIFO except for explicit `BringToFront`.
- No deduplication means duplicate pushes can lead to duplicate work unless higher layers prevent it.
- `Jobs` assumes positive page/perpage values. Invalid values could produce unexpected slice behavior because the method does not validate inputs.
- `jobQueueEntry.size` and `modified` are not used by this file, so callers should not expect internal sorting by size or modification time.
- Long queues make `BringToFront` O(n) and use slice shifting; benchmarks cover this but it is not optimized for extremely frequent arbitrary promotions.

## Test Signals

`queue_test.go` validates push/pop/done lifecycles, absent `Done` calls, empty queue behavior, explicit bring-to-front ordering including first and last elements, and pagination across queued-only and mixed progress/queued states. Benchmarks cover arbitrary bumping in a 10k queue and push/pop/done throughput for 10k files.
