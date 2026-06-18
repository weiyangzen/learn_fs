# sources/storage-engines/foundationdb/fdbclient/include/fdbclient/Knobs.h

## Purpose
Declares all client-side FoundationDB knobs and helper functions for initialization, reset, parsing, and dynamic assignment. `ClientKnobs` is the central configuration object controlling client retry timing, caches, transaction limits, backup/bulk operation behavior, blob-store limits, tracing, throttling, locking, and checksums.

## Important APIs, Types, And Functions
`Randomize` and `IsSimulated` boolean params drive construction. `getSimulatedTxnTimeoutSeconds()` returns simulation-only timeout values. `ClientKnobs` inherits `KnobsImpl<ClientKnobs>` and declares hundreds of typed fields, including transaction limits, key/value size limits, location cache settings, KRM limits, watch limits, backup/restore/bulk load/dump settings, dynamic knob timeouts, client status sampling, blob-store knobs, consistency-check settings, CLI settings, trace limits, tag throttling, range-lock retry behavior, and checksum flags. Global APIs include `CLIENT_KNOBS`, `getClientKnobs()`, `resetClientKnobs()`, `initializeClientKnobs()`, `tryParseClientKnobValue()`, `parseClientKnobValue()`, `trySetClientKnob()`, `setClientKnob()`, and `setupClientKnobs()`.

## Control Flow
Startup initializes `CLIENT_KNOBS` with deterministic or randomized values depending on simulation mode. Parsing functions convert strings into `KnobValue` using the target knob's expected type. Setter functions update named knobs or throw/fail depending on strictness. Consumers read `CLIENT_KNOBS` directly throughout fdbclient code.

## State And Persistence Behavior
`CLIENT_KNOBS` is a process-global pointer to immutable-looking but resettable client knob state. Knobs themselves are process memory, though parsed values can originate from config, command-line options, environment, or dynamic cluster metadata. Reset/reinitialize changes subsequent behavior globally.

## Dependencies And Integration Points
The header depends on `KnobValue.h`, Flow boolean params, and Flow knob infrastructure. It is integrated everywhere in fdbclient, including blob store defaults, location cache behavior, KRM limits, backup/bulk paths, status sampling, throttling, and transaction timeout logic.

## Risks And Test Signals
Risks include global state ordering, simulation randomization changing expected behavior, parsing drift after adding knobs, unsafe runtime changes to values assumed constant, and broad blast radius from default changes. Test signals should include knob initialization in simulation and non-simulation, parse/set for representative fields, dynamic knob update tests, blob-store knob URL overrides, transaction timeout behavior, and compile-time coverage for new fields in initialization.
