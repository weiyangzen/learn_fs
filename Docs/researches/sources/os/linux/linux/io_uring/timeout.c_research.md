# File Research: sources/os/linux/linux/io_uring/timeout.c

io_uring timeout and linked-timeout implementation. This file manages hrtimer-backed timeout requests, timeout removal/update, completion-sequence timeouts, multishot timeouts, linked timeout cancellation, and timeout teardown.

Key responsibilities:
- Parses relative/absolute/immediate timeout values and clock flags.
- Implements regular timeouts, completion-count-based timeouts, multishot timeouts, and linked timeouts.
- Maintains regular and linked timeout lists under `ctx->timeout_lock`.
- Cancels, updates, flushes, and kills timeouts by user data/task/ring teardown.
- Disarms linked timeouts as linked requests complete or fail.
- Fails dependent links when a non-hardlink request fails.

Important data flows:
- Timeout prep allocates async timeout data, validates flags, parses time, sets hrtimer function, records sequence offset/repeats, and links timeout metadata.
- `io_timeout()` inserts regular timeouts either as no-sequence entries or sorted by target CQ sequence, then starts the hrtimer.
- Hrtimer callbacks remove list entries, update timeout counters, set result/fail state, and queue task_work completion.
- Linked timeout expiry grabs a ref on the previous linked request if possible, splices itself out, then task_work attempts cancellation of the target request.
- Timeout remove either cancels by user data or updates regular/linked timer expiry.

Concurrency and locking:
- `timeout_lock` protects timeout lists and timer/list state.
- `completion_lock` is required with `timeout_lock` for linked request matching and ordering.
- Request refs protect linked previous requests during timeout-driven cancellation.
- Hrtimer cancellation handles `-1` as already-running callback and reports `-EALREADY`.

Important invariants:
- More than one timeout clock flag is invalid.
- Multishot timeouts cannot be absolute.
- Linked timeout SQEs cannot specify completion-count offsets and must follow an existing link head.
- `cq_timeouts` adjusts completion-count timeout sequencing so timeout CQEs do not count incorrectly.
