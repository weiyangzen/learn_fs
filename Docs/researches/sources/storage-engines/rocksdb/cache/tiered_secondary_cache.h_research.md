# sources/storage-engines/rocksdb/cache/tiered_secondary_cache.h

## Purpose
Defines `TieredSecondaryCache`, a `SecondaryCacheWrapper` that stacks a compressed secondary cache above an NVM/local-flash secondary cache. Its policy is asymmetric: blocks read directly from SSTs can warm the NVM tier through `InsertSaved`, and hits in NVM can be promoted toward compressed secondary and primary block caches, but evictions from upper tiers are not demoted.

## Important APIs and Types
The constructor accepts compressed and NVM `SecondaryCache` instances plus a `TieredAdmissionPolicy`; debug builds assert the three-queue admission policy. `Insert` is intentionally a no-op returning OK, while `InsertSaved` forwards saved compressed bytes to `nvm_sec_cache_`. `Lookup` and `WaitAll` are declared here and coordinate the multi-tier read path. Private `CreateContext` carries key, erase advice, helper, inner create context/handle, compressed-cache pointer, and statistics. `ResultHandle` wraps an inner async handle and exposes `IsReady`, `Wait`, `Size`, and `Value`.

## Control Flow and State
`ResultHandle::IsReady` completes when the inner handle becomes ready, transferring size/value and dropping the inner handle. The helper returned by `GetHelper()` installs `MaybeInsertAndCreate` as a create callback while other callbacks assert, because this helper should only bridge creation/promotion behavior. Persistent state is not owned here; the durable-like state lives in the underlying NVM cache. Risks include relying on callback assertions to catch invalid helper use, debug-only policy enforcement, and careful lifetime management of the nested result handle. Test coverage is in `tiered_secondary_cache_test.cc`.
