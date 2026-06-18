# sources/object-store/rustfs/crates/ecstore/src/store/heal.rs

## Purpose
Implements `ECStore` heal handlers across pools. It aggregates format healing, delegates bucket healing to peers, runs object healing across active pools, and checks abandoned multipart parts.

## Important APIs, Types, And Functions
Constants define structured logging fields/events for heal operations. Handler methods are `handle_heal_format`, `handle_heal_bucket`, `handle_heal_object`, and `handle_check_abandoned_parts`.

## Control Flow
`handle_heal_format` initializes an aggregate `HealResultItem`, calls each pool’s `heal_format`, counts `NoHealRequired`, appends before/after drive states, logs completion, and returns `NoHealRequired` only if all pools did. `handle_heal_object` logs the start event, encodes directory-object names, skips suspended pools, runs pool heal calls concurrently, decodes result object names, returns the first success, then the first non-not-found error, and finally synthesizes file/version not found. `handle_check_abandoned_parts` delegates to the only pool or checks every pool and returns the first error.

## State And Persistence Behavior
This file mostly coordinates. Actual format writes occur in `Sets::heal_format`; actual object repair occurs in `SetDisks::heal_object`; peer bucket heal may create missing bucket structure.

## Dependencies And Integration Points
Depends on pool routers, peer system, heal options/results, object path encode/decode helpers, suspension checks, error classifiers, and tracing logs. It is the implementation behind `ECStore`’s `HealOperations` trait.

## Risks
The loop selecting the first non-not-found error uses an immediate `return match` inside a `for`; because `continue` is inside the match arm, it still scans not-found errors, but the structure is easy to misread and should be handled carefully in edits. Result vectors are sized by futures actually pushed, not all pools, while `errs` capacity uses all pools. Suspended pools are silently skipped.

## Test Signals
No direct tests in this file. Useful tests would cover multi-pool success/error precedence, all-pools not found, suspended pool skipping, object name encode/decode, and aggregate `NoHealRequired` behavior.
