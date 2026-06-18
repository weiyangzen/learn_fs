# File Research: sources/os/linux/linux/block/blk-flush.c

## Scope

This file implements sequencing for block requests with `REQ_PREFLUSH` and/or `REQ_FUA`, translating them into optional preflush, data, and postflush phases according to queue write-cache and FUA capabilities.

## Core APIs and Entry Points

- Flush state machine:
  - `blk_insert_flush()` inserts a request into flush sequencing or lets it continue normally.
  - `blk_flush_complete_seq()` advances one request through its next phase.
  - `blk_kick_flush()` decides when to issue the shared flush request.
  - `flush_end_io()` completes the shared flush request and advances all requests waiting on it.
  - `mq_flush_data_end_io()` handles completion of the data phase for sequenced requests.
- Utilities:
  - `is_flush_rq()` identifies the shared flush request by end_io callback.
  - `blkdev_issue_flush()` submits a synchronous flush bio.
  - `blk_alloc_flush_queue()`, `blk_free_flush_queue()`.
  - `blk_mq_hctx_set_fq_lock_class()` lets drivers customize flush lockdep class.

## Major State

- Sequence bits:
  - `REQ_FSEQ_PREFLUSH`, `REQ_FSEQ_DATA`, `REQ_FSEQ_POSTFLUSH`, `REQ_FSEQ_DONE`.
- `struct blk_flush_queue` owns:
  - double-buffered `flush_queue[2]`,
  - pending/running indexes,
  - `flush_pending_since`,
  - `flush_data_in_flight`,
  - shared `flush_rq`,
  - `mq_flush_lock`,
  - saved flush request status.

## Control Flow

- `blk_insert_flush()` computes required policy:
  - data phase if the request has sectors,
  - preflush if writeback cache exists and `REQ_PREFLUSH` is set,
  - postflush if writeback cache exists, `REQ_FUA` is set, and hardware lacks FUA.
- It clears `REQ_PREFLUSH` and unsupported `REQ_FUA` before driver submission, and sets `REQ_SYNC` to preserve accounting semantics.
- Requests needing only data return false and proceed normally.
- Requests needing pre/post flush enter the state machine with `RQF_FLUSH_SEQ` and a saved original end_io.
- Double-buffering lets multiple requests wait on one shared `REQ_OP_FLUSH` request. `blk_kick_flush()` issues a flush only when no other flush is running and either no data phase is in flight or pending flushes have waited past `FLUSH_PENDING_TIMEOUT`.
- The shared flush request borrows tag/internal tag context from the first pending request and is submitted through the queue requeue path.
- Data-phase completion restores queue list state, decrements in-flight data, and advances to postflush or done.
- Final completion restores the original request bio/end_io state and calls `blk_mq_end_request()`.

## Dependencies

- blk-mq request lifecycle, tags, requeue list, scheduler restart, and request initialization.
- Queue feature flags `BLK_FEAT_FUA` and write-cache state.
- Partition stats for flush accounting.

## Risks and Invariants

- Flush/FUA requests must not be normally merged; the code warns if `rq->bio != rq->biotail`.
- Sequenced data requests are completed twice internally, but bio submitters are notified only after the full flush sequence completes.
- The state machine requires `fq->mq_flush_lock` for sequence/queue transitions.
- The shared flush request is reused and must be marked idle only after true completion because timeout paths may call its end_io.
- Tag borrowing differs for scheduler vs no-scheduler queues and must be unwound correctly.
