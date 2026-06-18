# sources/storage-engines/tikv/src/coprocessor/interceptors/deadline.rs

Purpose: wraps a future with deadline checks before every poll. It is a small interceptor used to stop yieldable coprocessor work after its request deadline.

Important APIs/types: `check_deadline(fut, deadline)` returns `DeadlineChecker<F>`, a pinned future whose `poll` calls `deadline.check()?` before polling the inner future and maps a ready inner result into `Ok`.

State and persistence: only the inner future and `Deadline` are stored. There is no persistent state. Dependencies are `tikv_util::deadline::{Deadline, DeadlineError}` and `pin_project`.

Integration points: `Endpoint::handle_unary_request_impl` wraps `handler.handle_request()` before tracking and optional semaphore limiting. Streaming code currently performs explicit deadline checks around scheduling and snapshot, but not this per-poll wrapper around each streaming handler call. Risks: non-yielding blocking work cannot be interrupted until it returns to poll; callers must convert `DeadlineError` into coprocessor `Error::DeadlineExceeded`. The local Tokio test verifies short work succeeds and long yieldable work returns a deadline error.
