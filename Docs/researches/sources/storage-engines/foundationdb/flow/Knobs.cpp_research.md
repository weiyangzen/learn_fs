# sources/storage-engines/foundationdb/flow/Knobs.cpp

## Purpose
Bootstraps and manages Flow runtime/simulation knobs, including defaults, randomized buggify variants, typed parsing, setting, getting, tracing, and parser tests.

## Important APIs, Types, And Functions
`FlowKnobs::FlowKnobs()`, `FlowKnobs::initialize()`, global `bootstrapGlobalFlowKnobs`, `FLOW_KNOBS`, and `resetFlowKnobs()` define global configuration. `Knobs::parseKnobValue()`, typed `setKnob()` overloads, `getKnob()`, `initKnob()` overloads, and `trace()` implement typed registry behavior. Helpers `toLower()`, `safe_stod()`, `safe_stoi()`, `safe_stoi64()`, and `safe_stob()` validate string conversions.

## Control Flow
Initialization calls `INIT_KNOB` repeatedly for timing, tracing, metrics, networking, TLS, file I/O, simulation, load balancing, encryption, and REST settings. Many knobs adjust when `randomize && buggify()`. `initKnob()` only overwrites values not explicitly set, preserving user overrides across reinitialization. Parsing dispatches by knob membership in typed maps and returns `NoKnobFound` for unknown names.

## State And Persistence Behavior
State is process-global and in-memory: knob values, typed maps pointing at value storage, and the `explicitlySetKnobs` set. `trace()` emits current values as TraceEvents; no persistent config is written here.

## Dependencies And Integration Points
Depends on encryption utilities for randomized auth-token algorithm, Flow errors, deterministic random/buggify, BooleanParam, UnitTest, and Trace. Practically every Flow subsystem reads `FLOW_KNOBS`.

## Risks And Edge Cases
The file is a high-blast-radius default table; type mistakes or changed defaults affect many subsystems. Explicitly-set tracking is lower-case, so all lookups must be normalized consistently. Parser helpers rely on full-string consumption and convert all parse errors to `invalid_option_value`. Randomized buggify defaults can hide assumptions if tests are not deterministic.

## Test Signals
`/flow/Knobs/ParseKnobValue` validates basic double/int/int64/bool parsing and invalid suffix rejection. Broader signals come from simulation runs that trace knobs and exercise randomized branches.
