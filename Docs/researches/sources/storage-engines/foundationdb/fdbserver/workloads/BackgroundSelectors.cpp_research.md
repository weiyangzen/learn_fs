# sources/storage-engines/foundationdb/fdbserver/workloads/BackgroundSelectors.cpp

Purpose: defines `BackgroundSelectors`, a background consistency workload for key selectors. It continuously compares `getKey()` selector results with bounded `getRange()` results to catch selector/range disagreement under concurrent database activity.

Important APIs, types, and functions: `randomizedSelector()` sometimes rewrites an `orEqual` selector into an equivalent `keyAfter(key)` form. `BackgroundSelectorWorkload` extends `TestWorkload`; constructor options include `testDuration`, `actorsPerClient`, `maxDiff`, `minDiff` (used for `minDrift`), `transactionsPerSecond`, and fixed `resultLimit=100`. `backgroundSelectorWorker()` owns the selector/range loop. Metrics report approximate transactions and actors.

Control flow: `start()` launches `actorsPerClient` workers and waits for `testDuration`. Each worker repeatedly chooses forward or backward direction, obtains initial boundary keys with `getKey()`, then periodically selects drift offsets and a range length (`diff`). It fetches the range between randomized selectors and separately fetches start/end selector results. If the returned range is shorter than the limit and not truncated by the beginning sentinel, it verifies that first and last keys match the independent selector results.

State and persistence behavior: no data is written by this workload. It reads `allKeys`, user/system boundaries, and live key contents through ordinary transactions. Worker state is entirely in memory: start/end keys, drifts, diff, direction, and restart flags.

Dependencies and integration points: uses `NativeAPI.actor.h`, `TesterInterface`, Flow coroutine transactions, `KeySelectorRef`, `keyAfter`, `allKeys`, and tester workload scheduling. It is intended to run alongside data-mutating workloads, increasing coverage of selector semantics under changing keyspaces.

Risks and edge cases: both `minDrift` and `maxDrift` are read from the `"minDiff"` option, which appears accidental and means a configured max drift option would be ignored. Empty ranges or limit-truncated ranges cause restarts or reduce checking strength. Because data can change between retries, correctness depends on each validation transaction seeing a consistent snapshot.

Test signals: `check()` scans worker futures for errors. Main correctness failures emit `BackgroundSelectorError` with direction, drift, diff, range size, expected selector result, and actual boundary key.
