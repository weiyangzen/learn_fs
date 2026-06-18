# sources/storage-engines/rocksdb/utilities/fault_injection_secondary_cache.h

## Purpose
This header declares `FaultInjectionSecondaryCache`, a `SecondaryCache` decorator that randomly fails inserts and lookups for correctness testing under cache errors.

## Important APIs, types, and functions
The constructor accepts a base `SecondaryCache`, a seed, and a probability denominator. It detects a compressed secondary cache by comparing `base_->Name()` to `"CompressedSecondaryCache"`, setting `base_is_compressed_sec_cache_`.

The public interface implements `Name`, `Insert`, `InsertSaved`, `Lookup`, `SupportForceErase`, `Erase`, `WaitAll`, capacity setters/getters, and printable options. `InsertSaved()` is a no-op returning OK, which is notable because it does not inject errors or forward saved compressed data to the base.

Nested `ResultHandle` implements `SecondaryCacheResultHandle` with `IsReady`, `Wait`, `Value`, `Size`, and static `WaitAll`. It retains the owning cache pointer, optional base handle, final value, and final size.

`ErrorContext` contains only a `Random`. `thread_local_error_` stores per-thread contexts and uses `DeleteThreadLocalErrorContext`.

## Control flow
Callers interact through the normal `SecondaryCache` API. Inserts and lookup readiness draw random decisions from the thread-local context. Delegating methods bypass injection and forward directly to the base cache.

## State and persistence behavior
The header defines wrapper-local configuration (`base_`, `seed_`, `prob_`, compressed-cache flag) and per-thread random state. It does not own persistent cache data; persistence and memory management for entries remain in `base_`.

## Dependencies and integration points
It includes `rocksdb/secondary_cache.h`, `util/random.h`, and `util/thread_local.h`. The class lives in `ROCKSDB_NAMESPACE` and can be plugged into DB options wherever a secondary cache is accepted.

## Risks and edge cases
The compressed-cache name check is string-based and may miss subclasses or renamed implementations. `InsertSaved()` returning OK without forwarding can make saved-object paths appear successful while dropping data. Probability validation is external. Result-handle lifetime assumes the parent cache outlives all handles.

## Test signals
The header has no direct unit test in this subset; behavior should be inferred from tests or stress configurations that exercise secondary cache failures.
