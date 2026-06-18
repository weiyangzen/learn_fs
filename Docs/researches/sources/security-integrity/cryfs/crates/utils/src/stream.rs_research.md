# sources/security-integrity/cryfs/crates/utils/src/stream.rs

Purpose: Supplies async stream helpers that process every item even when failures occur, returning the first error while logging later errors. This is useful for cleanup or batch operations where fail-fast behavior would leave work unattempted.

Important APIs and types: `run_to_completion<E>` accepts a `Stream<Item = Result<(), E>>` and returns `Result<(), E>`. `for_each_unordered<T, E, F>` maps an iterator into a `FuturesUnordered` of async operations and delegates to `run_to_completion`.

Control flow: `run_to_completion` filters successful results out of the stream, pins the resulting error stream, stores the first error, logs subsequent errors, and continues polling until exhaustion. At the end it returns the saved first error or `Ok(())`. `for_each_unordered` collects all futures immediately, so all work can run concurrently, then drains that unordered stream.

State and persistence behavior: There is no persistence. In-memory state is the first error slot and the futures/stream being polled. Later errors are only observable via logs.

Dependencies and integration points: Uses `futures::stream`, `FuturesUnordered`, `StreamExt`, `future::ready`, `anyhow::Result` type naming, and the `log` crate. It fills the niche that `try_for_each_concurrent` does not because it avoids early cancellation.

Risks: Only the first error is returned; subsequent failures are lossy except for logs. `for_each_unordered` has no concurrency limit and collects every future, so very large iterators may create too much pending work. Because all futures are created upfront, side effects can start broadly once polled.

Test signals: Tokio tests cover all-success streams, single and multiple errors, empty streams, unordered iterator processing success, first-error return, and empty iterators.

Source-read signal: Read `sources/security-integrity/cryfs/crates/utils/src/stream.rs` completely for this pass (152 lines, 5013 bytes).
