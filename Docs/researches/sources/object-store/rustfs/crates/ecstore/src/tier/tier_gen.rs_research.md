# sources/object-store/rustfs/crates/ecstore/src/tier/tier_gen.rs

## Purpose

Generated/stub extension for `TierConfigMgr` message sizing.

## Important APIs and Types

Adds `TierConfigMgr::msg_size(&self) -> usize`, returning constant `100`.

## Control Flow

No meaningful control flow; method is `dead_code`.

## State and Persistence Behavior

No state; size is not derived from actual config.

## Dependencies and Integration Points

Only depends on `TierConfigMgr`. Future generated serialization could use it.

## Risks and Edge Cases

The constant is inaccurate for real configs if used for allocation or encoding limits.

## Test Signals

No tests.
