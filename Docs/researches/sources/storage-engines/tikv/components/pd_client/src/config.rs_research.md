# sources/storage-engines/tikv/components/pd_client/src/config.rs

## Purpose
`config.rs` defines `pd_client::Config`, the runtime configuration for PD endpoint connection and refresh behavior.

## Important APIs, Types, and Functions
`Config` contains endpoints, retry interval/count/log throttling, update interval, and forwarding enablement. `Default` chooses `127.0.0.1:2379`, 300 ms retry interval, unlimited retries represented by `isize::MAX`, log every 10 duplicate retry errors, 10 minute update interval, and forwarding disabled. `new` overrides endpoints. `validate` rejects empty endpoints, `retry_log_every == 0`, and `retry_max_count < -1`.

## Control Flow
Validation is straight-line guard checks returning boxed errors. Client constructors interpret `retry_max_count == -1` as infinite and otherwise add one retry attempt.

## State and Persistence Behavior
The struct is serializable/deserializable and cloneable but holds no live connection state. It feeds PD client initialization and reconnect loops.

## Dependencies and Integration Points
Uses serde and `tikv_util::config::ReadableDuration`. It is consumed by both v1 and v2 PD clients and by higher-level TiKV config loading.

## Risks
The documentation says default retry max is represented by `-1`, while the `Default` implementation uses `isize::MAX`; constructors handle `-1` specially elsewhere. Misconfigured `retry_log_every` would otherwise cause modulo/division problems, hence validation rejects zero.

## Test Signals
`test_pd_cfg` validates the default config.
