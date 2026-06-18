# sources/storage-engines/foundationdb/fdbclient/ClientKnobs.cpp

## Purpose

`ClientKnobs.cpp` owns initialization, parsing, and mutation of client-side FoundationDB knobs. These knobs control retry/backoff behavior, location cache sizes, task-bucket and backup behavior, blobstore IO limits, dynamic configuration timeouts, client status reporting, transaction tag throttling, consistency checking, CLI behavior, and simulation randomization.

## Important APIs, Types, And Functions

`ClientKnobs::ClientKnobs()` delegates to `initialize()`. Global state is held by `globalFlowKnobs`, `globalClientKnobs`, `bootstrapGlobalClientKnobs`, and the exported pointer `CLIENT_KNOBS`, initially pointed at the bootstrap instance. `resetClientKnobs()` resets Flow and client knobs to the global mutable instances, while `initializeClientKnobs()` reinitializes the current instances in place.

`tryParseClientKnobValue()` and `parseClientKnobValue()` first ask `FLOW_KNOBS`, then `CLIENT_KNOBS`, to parse a named string value. `trySetClientKnob()` applies a typed `KnobValueRef` to both Flow and client knob sets and reports whether either accepted the name. `setClientKnob()` throws `invalid_option_value` and traces `FailedToSetKnob` on failure. `setupClientKnobs()` is the user-facing batch path; it catches invalid names/values, prints warnings, traces them, and rethrows only unexpected errors.

`ClientKnobs::initialize()` is a long table of `INIT_KNOB` assignments. Many defaults are conditionally perturbed under `randomize && buggify()` to stress simulation: for example proxy counts can drop to one, cache sizes can shrink, timeouts can shorten, and blobstore or consistency-check behavior can vary. `getSimulatedTxnTimeoutSeconds()` feeds simulated transaction lifetime selection.

## Control Flow

Initialization is single-pass and intentionally order-sensitive where knobs derive from earlier values, such as task-bucket timeout versions depending on `CORE_VERSIONSPERSECOND` and blobstore concurrency depending on `BACKUP_TASKS_PER_AGENT`. Parsing/setting paths use typed generated knob maps and reject unknown names. The file also preserves backwards compatibility by adding a `double_knobs` alias from `global_tag_throttling_rw_fungibility_ratio` to the newer non-global field.

## State And Persistence

Knobs are process-global in-memory configuration. They are not persisted here, but they materially influence persistent client/backup behavior by controlling transaction size, task durations, mutation block size, backup log/range partitioning, blobstore IO, and dynamic cluster configuration timeouts. Because the global pointers are mutable through reset/setup helpers, test and simulation code can change effective behavior process-wide.

## Dependencies And Integration Points

Dependencies include `fdbclient/Knobs.h`, Flow knobs, deterministic randomization, Flow unit tests, tracing, and generated knob metadata. The values are consumed throughout `fdbclient`, notably by `DatabaseBackupAgent.cpp`, commit proxy helpers, status reporting, blobstore/backup containers, transaction throttling, and CLI setup.

## Risks And Test Signals

Derived defaults can become stale if base knobs are changed after initialization. The included unit test `/fdbclient/knobs/initialize` explicitly verifies that reinitialization recomputes derived `TASKBUCKET_TIMEOUT_VERSIONS` after `CORE_VERSIONSPERSECOND` is set. Other risk areas are process-global mutation in multi-test environments, simulation-only buggify values hiding production assumptions, and compatibility aliases drifting from public option names.
