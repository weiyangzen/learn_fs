# sources/storage-engines/tikv/components/causal_ts/src/lib.rs

## Purpose
Crate root and public abstraction for causal timestamp providers.

## APIs, Types, And Functions
Exports config, errors, TSO implementation, and metrics. `CausalTsProvider` is an async trait with `async_get_ts` and `async_flush`. `CausalTsProviderImpl` uses `enum_dispatch` to wrap production `BatchTsoProvider<pd_client::RpcClient>`, test provider variants, and `TestProvider`.

## Control Flow
Consumers call the trait methods without knowing the provider implementation. `async_flush` is explicitly for causality-sensitive events such as leader transfer, where cached timestamps must be discarded and a new timestamp returned.

## State And Persistence
The root file has no state. The nested test provider uses an atomic timestamp starting at 100 and increments or jumps by 100 on flush.

## Dependencies And Integration Points
Uses `async_trait`, `enum_dispatch`, `txn_types::TimeStamp`, PD client types, and test PD client under test/testexport. CDC depends on this crate for causal timestamp behavior.

## Risks And Test Signals
Trait semantics are important: providers must return monotonically valid timestamps and flush must enforce causality. The test provider's fixed jump size is part of unit-test expectations and should not be changed casually.
