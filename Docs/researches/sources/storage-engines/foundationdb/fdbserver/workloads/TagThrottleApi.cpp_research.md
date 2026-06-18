# sources/storage-engines/foundationdb/fdbserver/workloads/TagThrottleApi.cpp

## Purpose
`TagThrottleApiWorkload` fuzzes the tag throttling management API by randomly throttling, unthrottling, listing, and toggling auto-throttling for debug transaction tags. It checks API invariants for manual and automatic throttles.

## Important APIs, Types, and Functions
It uses `ThrottleApi::throttleTags()`, `unthrottleTags()`, `getThrottledTags()`, `getRecommendedTags()`, `unthrottleAll()`, and `enableAuto()`. It tracks expected manual state in `std::map<std::pair<TransactionTag, TransactionPriority>, TagThrottleInfo>`, chooses tags from `DatabaseContext::debugTransactionTagChoices`, and references `allTransactionPriorities`, `TagThrottleType`, `TagThrottleInfo`, `TagSet`, and `SERVER_KNOBS` throttle limits.

## Control Flow
`setup()` enables debug tag use. Client 0 runs `runThrottleApi()` under a timeout for `testDuration`. Each loop sleeps up to five seconds, chooses one of six actions, and executes the corresponding actor: add a manual throttle, remove one tag, list and validate active tags, remove a group, enable/disable auto throttling, or list recommended auto tags.

## State and Persistence Behavior
Persistent state is the cluster tag throttle configuration maintained by `ThrottleApi`. Local state is the expected map of manually throttled tags, including expiration time and priority. Auto-throttle enabled state is tracked locally in `autoThrottleEnabled` after API calls.

## Dependencies and Integration Points
The workload integrates with FDB client tag throttling internals, transaction priorities, database context debug tags, server knobs for maximum manual/auto throttles, and simulator timing through `now()`.

## Risks and Edge Cases
The expected manual map uses wall-clock expiration comparisons, so timing races around expiry can make assertions delicate. The code asserts that `too_many_tag_throttles` only happens when the local manual map size has reached the server knob limit. `getTags()` treats AUTO entries specially and validates max counts; if background auto throttling is disabled or timing changes, assertions can become seed-sensitive.

## Test Signals
Assertions inside every API path are the main signal. `check()` always returns true, so test failure is assertion-driven. Useful coverage includes manual limit handling, priority-specific and all-priority unthrottles, auto recommendation type validation, and auto enable/disable behavior.
