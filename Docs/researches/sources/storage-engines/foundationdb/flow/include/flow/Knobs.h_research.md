# sources/storage-engines/foundationdb/flow/include/flow/Knobs.h

## Purpose
`Knobs.h` defines Flow's configurable runtime knob registry and the `FlowKnobs` collection of network, tracing, storage, TLS, metrics, simulation, encryption, and load-balancing settings.

## Important APIs, Types, And Functions
Important items are `INIT_KNOB`, `NoKnobFound`, `ParsedKnobValue`, base `Knobs`, `KnobsImpl<T>`, `FlowKnobs`, `bootstrapGlobalFlowKnobs`, `FLOW_KNOBS`, and `resetFlowKnobs()`. `Knobs` exposes typed `setKnob()`, `getKnob()`, `parseKnobValue()`, and `trace()`.

## Control Flow
Derived `initialize()` methods register knob member addresses through `initKnob()`. `setKnob()` looks up by name and type, writes the pointed-to value, and records explicit settings. `reset()` clears explicit settings and reinitializes defaults using randomization/simulation inputs.

## State And Persistence Behavior
State includes maps from knob names to member pointers by type plus the actual `FlowKnobs` member values and explicit-set names. A bootstrap global is available before normal knob collections exist.

## Dependencies And Integration Points
It depends on `Platform`, maps, sets, variants, optionals, and strings. `FLOW_KNOBS` is read across networking, files, tracing, TLS, metrics, simulation, encryption, HTTP, and load balancing.

## Risks And Edge Cases
Knob names are stringly typed and type-specific; mismatches fail. Because maps store raw member pointers, reinitialization must preserve object lifetime. Randomized knobs can affect simulation determinism. Global pointer usage makes initialization order important.

## Test Signals
Tests should cover setting/parsing every supported type, explicit-set tracking, reset behavior, trace output, randomized/simulated initialization, unknown knob handling, and representative consumers reading updated values.
