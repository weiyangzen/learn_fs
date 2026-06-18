# sources/storage-engines/tikv/components/causal_ts/src/config.rs

## Purpose
Defines user-facing configuration for `BatchTsoProvider`.

## APIs, Types, And Functions
`Config` contains `renew_interval`, `renew_batch_min_size`, `renew_batch_max_size`, and `alloc_ahead_buffer`. `validate` rejects zero interval, zero min/max batch size, and zero allocation-ahead buffer. `Default` maps to constants from `tso.rs`.

## Control Flow
Configuration is deserialized with kebab-case names and passed into provider construction by surrounding TiKV code. Validation prevents nonsensical production settings; tests can still call lower-level constructors with zero renewal interval to disable background renewal.

## State And Persistence
The struct is serializable and likely persisted in TiKV config. Runtime provider state is derived from it, including cache multiplier and batch size bounds.

## Dependencies And Integration Points
Uses serde derives and `ReadableDuration`. Depends on `crate::tso` constants for defaults.

## Risks And Test Signals
Incorrect validation could permit providers that never renew or request zero TSOs. The code-level defaults encode operational assumptions about PD throughput and desired failure tolerance.
